from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RentalOrderViewSet, RentalOrderLineViewSet, ReservationViewSet, DeliveryViewSet

router = DefaultRouter()
router.register(r'orders', RentalOrderViewSet, basename='rental-order')
router.register(r'lines', RentalOrderLineViewSet, basename='rental-order-line')
router.register(r'reservations', ReservationViewSet, basename='reservation')
router.register(r'deliveries', DeliveryViewSet, basename='delivery')

urlpatterns = [
	path('', include(router.urls)),
]