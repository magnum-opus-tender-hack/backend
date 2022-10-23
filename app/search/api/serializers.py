from rest_framework import serializers
from django.core.validators import MinLengthValidator, MinValueValidator

from search.models import Product, UnitCharacteristic, Characteristic


class QueryFilterSerializer(serializers.Serializer):
    value = serializers.CharField(max_length=100)
    type = serializers.CharField(max_length=100)

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError


class SearchSerializer(serializers.Serializer):
    body = serializers.ListSerializer(child=QueryFilterSerializer())
    limit = serializers.IntegerField(default=5, min_value=1)
    offset = serializers.IntegerField(default=0, min_value=0)

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
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError


class HintResponseSerializer(serializers.Serializer):
    type = serializers.CharField()
    content = serializers.CharField()

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError


class AutoCompleteRequestSerializer(serializers.Serializer):
    content = serializers.CharField(validators=[MinLengthValidator(3)])
    exclude = serializers.ListSerializer(child=QueryFilterSerializer(), default=[])

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError


class AutoCompleteSerializerNode(serializers.Serializer):
    coordinate = serializers.IntegerField(validators=[MinValueValidator(0)])
    value = HintResponseSerializer()

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError


class AutoCompleteResponseSerializer(serializers.Serializer):
    nodes = serializers.ListField(child=AutoCompleteSerializerNode())

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError


class CharacteristicSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ["name", "value"]
        model = Characteristic


class UnitCharacteristicSerializer(serializers.ModelSerializer):
    value = serializers.SerializerMethodField("get_value_n")

    def get_value_n(self, obj):
        return obj.num_value

    class Meta:
        fields = ["name", "value", "unit"]
        model = UnitCharacteristic


class ProductSerializer(serializers.ModelSerializer):
    characteristic = serializers.SerializerMethodField("get_characteristic_n")

    def get_characteristic_n(self, obj: Product):
        return (
            CharacteristicSerializer(
                Characteristic.objects.filter(products__product=obj), many=True
            ).data
            + UnitCharacteristicSerializer(
                UnitCharacteristic.objects.filter(products__product=obj), many=True
            ).data
        )

    class Meta:
        fields = ["id", "name", "score", "characteristic"]
        model = Product
