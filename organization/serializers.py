from .models import *
from rest_framework import serializers
from users.serializers import UsersSerializer


class OrganizationSerializers(serializers.ModelSerializer):
    admin = UsersSerializer(read_only=True)
    panel_access_url = serializers.CharField(read_only=True)

    class Meta:
        model = Organization
        fields = '__all__'

    def create(self, validated_data):
        validated_data['admin'] = self.context['request'].user
        unique_url = validated_data.get('name').replace(" ", "-").lower()
        count = Organization.objects.filter(panel_access_url=unique_url).count()
        if count > 0:
            unique_url = unique_url + "-" + str(count + 1)
        validated_data['panel_access_url'] = unique_url
        return Organization.objects.create(**validated_data)


class MembersSerializers(serializers.ModelSerializer):
    user = UsersSerializer(read_only=True)
    added_by = UsersSerializer(read_only=True)

    class Meta:
        model = Members
        fields = '__all__'

    def create(self, validated_data):
        validated_data['added_by'] = self.context['request'].user
        validated_data['user'] = self.context['request'].user
        return Members.objects.create(**validated_data)
