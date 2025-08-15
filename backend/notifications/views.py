from django.shortcuts import render
from rest_framework import viewsets
from .models import NotificationSetting
from .serializers import NotificationSettingSerializer


# Create your views here.


class NotificationSettingViewSet(viewsets.ModelViewSet):
	queryset = NotificationSetting.objects.all()
	serializer_class = NotificationSettingSerializer
