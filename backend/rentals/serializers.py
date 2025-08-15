from rest_framework import serializers
from .models import RentalOrder, RentalOrderLine, Reservation, Delivery


class RentalOrderLineSerializer(serializers.ModelSerializer):
	class Meta:
		model = RentalOrderLine
		fields = '__all__'


class RentalOrderCreateLineInputSerializer(serializers.Serializer):
	product = serializers.IntegerField()
	quantity = serializers.IntegerField(default=1)
	unit = serializers.CharField(default='day')


class RentalOrderSerializer(serializers.ModelSerializer):
	lines = RentalOrderLineSerializer(many=True, read_only=True)

	class Meta:
		model = RentalOrder
		fields = '__all__'


class RentalOrderCreateSerializer(serializers.ModelSerializer):
	lines = RentalOrderCreateLineInputSerializer(many=True, write_only=True)
	expected_return_at = serializers.DateTimeField(required=False, allow_null=True)

	class Meta:
		model = RentalOrder
		fields = [
			'customer_name', 'customer_email', 'status',
			'start_at', 'end_at', 'expected_return_at', 'currency', 'lines'
		]


class ReservationSerializer(serializers.ModelSerializer):
	class Meta:
		model = Reservation
		fields = '__all__'


class DeliverySerializer(serializers.ModelSerializer):
	class Meta:
		model = Delivery
		fields = '__all__'