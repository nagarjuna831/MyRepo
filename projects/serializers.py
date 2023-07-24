from .models import *
from rest_framework import serializers
from users.serializers import UsersSerializer


class ProjectSerializer(serializers.ModelSerializer):
    user = UsersSerializer(read_only=True)
    class Meta:
        model = Project
        fields = '__all__'


    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        validated_data['billing'] =Billing.objects.get(user_id=self.context['request'].user)
        return Project.objects.create(**validated_data) 


