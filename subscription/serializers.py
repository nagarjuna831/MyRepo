from .models import *
from drf_writable_nested.serializers import WritableNestedModelSerializer
from rest_framework import serializers
from users.serializers import UsersSerializer
import re


class BillingSerializer(serializers.ModelSerializer):
    user =  UsersSerializer(read_only=True)
    class Meta:
        model = Billing
        fields = '__all__'
    

    def validate_duration(self, data):
        if data:
            if data != 365 and data != 30:
                raise serializers.ValidationError("Duration must be 365 or 30!")
        return data
    def validate_contact_no(self, data):
        regex = re.compile("(0|91)?[6-9][0-9]{9}")
        if regex.match(data):
            return data
        raise serializers.ValidationError("Invalid phone number !")

class BillingPaymentSerializer(serializers.ModelSerializer):
    
    class Meta:
        model= BillingPayment
        fields = '__all__'

class SubscriptionSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = SubscriptionModel
        fields = '__all__'