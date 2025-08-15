from django.shortcuts import render
from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from .models import Payment
from .serializers import PaymentSerializer


# Create your views here.


class PaymentViewSet(viewsets.ModelViewSet):
	queryset = Payment.objects.select_related('order').all()
	serializer_class = PaymentSerializer
	filter_backends = [DjangoFilterBackend]
	filterset_fields = ['order', 'gateway', 'status', 'is_deposit']
