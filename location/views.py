from django.shortcuts import render
from rest_framework import generics, viewsets, permissions, status
from .serializers import *
from .models import *
from datetime import date


class UserTrackingListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = UserTrackingSerializer
    queryset = UserTracking.objects.filter(is_delete=False)


class LocationRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = UserTrackingSerializer
    queryset = UserTracking.objects.filter(is_delete=False)
    lookup_field = 'id'


class LocationRetrieView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = UserTrackingSerializer
    
    def get_queryset(self):
        id=self.kwargs['id']
        Startdate=self.kwargs['startdate']
        Enddate=self.kwargs['enddate']
        return UserTracking.objects.filter(user=id).filter(is_delete=False).filter(date_added__date__range=(Startdate, Enddate))
