from rest_framework import serializers
from .models import Pricelist, PricelistItem


class PricelistItemSerializer(serializers.ModelSerializer):
	class Meta:
		model = PricelistItem
		fields = '__all__'


class PricelistSerializer(serializers.ModelSerializer):
	items = PricelistItemSerializer(many=True, read_only=True)

	class Meta:
		model = Pricelist
		fields = '__all__'