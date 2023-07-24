from .models import *
from rest_framework import serializers
from users.serializers import UsersSerializer


class UserTrackingSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserTracking
        fields = '__all__'
