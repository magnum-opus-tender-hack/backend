from rest_framework import serializers
from django.core.validators import MinLengthValidator, MinValueValidator


class QueryFilterSerializer(serializers.Serializer):
    value = serializers.CharField(max_length=100)
    type = serializers.CharField(max_length=100)

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError


class SearchSerializer(serializers.Serializer):
    body = serializers.ListSerializer(child=QueryFilterSerializer())

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


class AutoCompleteRequestSerializer(serializers.Serializer):
    content = serializers.CharField(validators=[MinLengthValidator(3)])


class AutoCompleteSerializerNode(serializers.Serializer):
    coordinate = serializers.IntegerField(validators=[MinValueValidator(0)])
    value = HintResponseSerializer()


class AutoCompleteResponseSerializer(serializers.Serializer):
    nodes = serializers.ListField(child=AutoCompleteSerializerNode())
