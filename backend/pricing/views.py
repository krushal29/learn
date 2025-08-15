from django.shortcuts import render
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Pricelist, PricelistItem
from .serializers import PricelistSerializer, PricelistItemSerializer


# Create your views here.


class PricelistViewSet(viewsets.ModelViewSet):
	queryset = Pricelist.objects.all()
	serializer_class = PricelistSerializer
	filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
	filterset_fields = ['active', 'currency', 'customer_group', 'region']
	search_fields = ['name']
	ordering_fields = ['name']


class PricelistItemViewSet(viewsets.ModelViewSet):
	queryset = PricelistItem.objects.select_related('pricelist', 'product').all()
	serializer_class = PricelistItemSerializer
	filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
	filterset_fields = ['pricelist', 'product', 'category', 'unit']
	search_fields = ['category', 'product__name', 'pricelist__name']
	ordering_fields = ['priority', 'base_price']
