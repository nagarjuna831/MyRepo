from rest_framework import serializers


class StatsSerializer(serializers.Serializer):
    form_count = serializers.IntegerField()
    file_count = serializers.IntegerField()
    workflow_count = serializers.IntegerField()
    project_count = serializers.IntegerField()
