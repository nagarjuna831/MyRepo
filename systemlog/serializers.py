from .models import *
from rest_framework import serializers
from users.serializers import UsersSerializer

class ActivityLogSerializer(serializers.ModelSerializer):
    actor = serializers.SerializerMethodField()
    model=serializers.SerializerMethodField()
    class Meta:
        model = ActivityLog
        fields = '__all__'
    
    def get_actor(self, obj):
        user = User.objects.filter(id=obj.actor.id)
        return UsersSerializer(user, many=True).data
    
    def get_model(self, obj):
        data=(str(obj.content_type))
        model=data.split()[-1]
        return model