from rest_framework import serializers
from fileupload.models import Files
from users.serializers import UsersSerializer


class FileSerializer(serializers.ModelSerializer):
    user = UsersSerializer(required=False)

    class Meta:
        model = Files
        fields = "__all__"

    def create(self, validated_data):
        user = self.context['request'].user
        if not user.is_anonymous:
            validated_data['user'] = self.context['request'].user
            return Files.objects.create(**validated_data)
        else:
            return Files.objects.create(**validated_data)


class FileSerializers(serializers.ModelSerializer):
    # user = UsersSerializer(required=False)

    class Meta:
        model = Files
        fields = "__all__"

    def create(self, validated_data):
        validated_data['user'] = None
        return Files.objects.create(**validated_data)
          