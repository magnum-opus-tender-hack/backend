from rest_framework import serializers


class SearchSerializer(serializers.Serializer):
    body = serializers.CharField(max_length=200)

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError


class ResponseSerializer(serializers.Serializer):
    results = serializers.JSONField()

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError


class HintRequestSerializer(serializers.Serializer):
    content = serializers.CharField()

    def create(self, validated_data):
        raise NotImplemented


class HintResponseSerializer(serializers.Serializer):
    type = serializers.CharField()
    content = serializers.CharField()
