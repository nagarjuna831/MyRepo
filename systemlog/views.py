from django.shortcuts import render
from rest_framework import generics, viewsets, permissions, status
from .serializers import *
from .models import *
from datetime import date


class ActivityLogListView(generics.ListAPIView):
    serializer_class =ActivityLogSerializer 
    queryset = ActivityLog.objects.all()

    def get_queryset(self):
        user = self.request.user.id
        return ActivityLog.objects.filter(actor_id=user)


class ActivityLogModelListView(generics.ListAPIView):
    serializer_class =ActivityLogSerializer 
    queryset = ActivityLog.objects.all()

    def get_queryset(self):
        model=self.kwargs['model']
        get_model(self)
        return ()
        return ActivityLog.objects.filter(content_type_model=self.kwargs['model'])


def get_model(self):
        model=self.kwargs['model']
        # data=ContentType.objects.filter(model=self.kwargs['model'])
        # print(data.__dict__ )
        # print(ContentType.objects.filter(model=self.kwargs['model']).model.name)            
        return ()                