from django.shortcuts import render
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.dateparse import parse_datetime
from django.db.models import Sum, Q
from django.db import transaction
from datetime import timedelta
from decimal import Decimal
from catalog.models import Product
from pricing.utils import compute_line_price
from .models import RentalOrder, RentalOrderLine, Reservation, Delivery
from .serializers import (
	RentalOrderSerializer,
	RentalOrderLineSerializer,
	ReservationSerializer,
	DeliverySerializer,
	RentalOrderCreateSerializer,
)


# Create your views here.


class RentalOrderViewSet(viewsets.ModelViewSet):
	queryset = RentalOrder.objects.all()
	serializer_class = RentalOrderSerializer
	filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
	filterset_fields = ['status', 'customer_email']
	search_fields = ['number', 'customer_name', 'customer_email']
	ordering_fields = ['created_at', 'start_at', 'end_at']

	def get_serializer_class(self):
		if self.action == 'create':
			return RentalOrderCreateSerializer
		return super().get_serializer_class()

	def create(self, request, *args, **kwargs):
		serializer = self.get_serializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		data = serializer.validated_data
		with transaction.atomic():
			order = RentalOrder.objects.create(
				customer_name=data['customer_name'],
				customer_email=data.get('customer_email', ''),
				status=data.get('status', 'draft'),
				start_at=data['start_at'],
				end_at=data['end_at'],
				expected_return_at=data.get('expected_return_at') or data['end_at'],
				currency=data.get('currency', 'USD'),
			)
			for line in data['lines']:
				product = Product.objects.get(id=line['product'])
				pricing = compute_line_price(product, order.start_at, order.end_at, line.get('unit', 'day'))
				RentalOrderLine.objects.create(
					order=order,
					product=product,
					quantity=line.get('quantity', 1),
					unit=line.get('unit', 'day'),
					duration_qty=pricing['duration_qty'],
					unit_price=pricing['unit_price'],
					rule_applied=pricing['rule'],
					subtotal=(pricing['subtotal'] * Decimal(line.get('quantity', 1))).quantize(Decimal('0.01')),
				)
			order.recalculate_totals()
		return Response(RentalOrderSerializer(order).data, status=status.HTTP_201_CREATED)

	@action(detail=False, methods=['post'], url_path='availability/check')
	def check_availability(self, request):
		product_id = request.data.get('product_id')
		quantity = int(request.data.get('quantity', 1))
		start_at = parse_datetime(request.data.get('start_at'))
		end_at = parse_datetime(request.data.get('end_at'))
		if not (product_id and start_at and end_at):
			return Response({'detail': 'product_id, start_at, end_at required'}, status=400)
		try:
			product = Product.objects.get(id=product_id)
		except Product.DoesNotExist:
			return Response({'detail': 'Product not found'}, status=404)

		buffer_start = start_at
		buffer_end = end_at
		if product.buffer_before_hours:
			buffer_start = buffer_start - timedelta(hours=product.buffer_before_hours)
		if product.buffer_after_hours:
			buffer_end = buffer_end + timedelta(hours=product.buffer_after_hours)

		conflicts = Reservation.objects.filter(
			product=product,
			status__in=['reserved', 'collected'],
		).filter(
			Q(start_at__lt=buffer_end) & Q(end_at__gt=buffer_start)
		).aggregate(total=Sum('quantity'))['total'] or 0

		available_qty = max(product.stock_quantity - conflicts, 0)
		return Response({
			'product_id': product.id,
			'requested_qty': quantity,
			'available_qty': available_qty,
			'is_available': available_qty >= quantity,
		})

	@action(detail=True, methods=['post'])
	def confirm(self, request, pk=None):
		order = self.get_object()
		if order.status not in ['draft', 'quoted']:
			return Response({'detail': 'Order cannot be confirmed from current state.'}, status=400)
		# Reserve inventory per line
		with transaction.atomic():
			for line in order.lines.all():
				Reservation.objects.create(
					product=line.product,
					order_line=line,
					start_at=order.start_at,
					end_at=order.end_at,
					quantity=line.quantity,
				)
			order.status = 'confirmed'
			order.save(update_fields=['status'])
			Delivery.objects.create(document_type='pickup', order=order, scheduled_at=order.start_at, items=[])
		return Response(RentalOrderSerializer(order).data)

	@action(detail=True, methods=['post'])
	def pickup(self, request, pk=None):
		order = self.get_object()
		if order.status != 'confirmed':
			return Response({'detail': 'Order is not in confirmed state.'}, status=400)
		Reservation.objects.filter(order_line__order=order, status='reserved').update(status='collected')
		order.status = 'out'
		order.save(update_fields=['status'])
		Delivery.objects.filter(order=order, document_type='pickup').update(status='done')
		return Response(RentalOrderSerializer(order).data)

	@action(detail=True, methods=['post'])
	def return_items(self, request, pk=None):
		order = self.get_object()
		if order.status not in ['out', 'confirmed']:
			return Response({'detail': 'Order is not out.'}, status=400)
		Reservation.objects.filter(order_line__order=order).update(status='returned')
		order.status = 'returned'
		order.actual_return_at = order.actual_return_at or order.end_at
		order.save(update_fields=['status', 'actual_return_at'])
		Delivery.objects.create(document_type='return', order=order, scheduled_at=order.end_at, items=[], status='done')
		return Response(RentalOrderSerializer(order).data)

	@action(detail=True, methods=['post'])
	def cancel(self, request, pk=None):
		order = self.get_object()
		if order.status in ['closed', 'cancelled']:
			return Response({'detail': 'Order already finalized.'}, status=400)
		Reservation.objects.filter(order_line__order=order, status__in=['reserved']).update(status='expired')
		order.status = 'cancelled'
		order.save(update_fields=['status'])
		return Response(RentalOrderSerializer(order).data)


class RentalOrderLineViewSet(viewsets.ModelViewSet):
	queryset = RentalOrderLine.objects.select_related('order', 'product').all()
	serializer_class = RentalOrderLineSerializer
	filter_backends = [DjangoFilterBackend]
	filterset_fields = ['order', 'product']


class ReservationViewSet(viewsets.ModelViewSet):
	queryset = Reservation.objects.select_related('order_line', 'product').all()
	serializer_class = ReservationSerializer
	filter_backends = [DjangoFilterBackend]
	filterset_fields = ['product', 'status']


class DeliveryViewSet(viewsets.ModelViewSet):
	queryset = Delivery.objects.select_related('order').all()
	serializer_class = DeliverySerializer
	filter_backends = [DjangoFilterBackend]
	filterset_fields = ['document_type', 'status']
