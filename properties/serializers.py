from rest_framework import serializers

from .models import (
    Location,
    Property,
    PropertyImage,
)


class DistanceField(serializers.Field):

    def to_representation(self, value):

        if value is None:
            return None

        return {
            "meters": round(value.m, 2),
            "kilometers": round(value.km, 3)
        }


class LocationSerializer(serializers.ModelSerializer):

    similarity = serializers.FloatField(
        read_only=True
    )

    class Meta:
        model = Location
        fields = [
            "id",
            "name",
            "slug",
            "country",
            "state",
            "city",
            "address",
            "point",
            "similarity",
        ]


class PropertyImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = PropertyImage
        fields = "__all__"


class PropertySerializer(serializers.ModelSerializer):
    images = PropertyImageSerializer(
        many=True,
        read_only=True
    )

    distance = DistanceField(
        read_only=True
    )

    similarity = serializers.FloatField(
        read_only=True
    )

    class Meta:
        model = Property

        fields = [
            "id",
            "location",
            "title",
            "slug",
            "description",
            "property_type",
            "status",
            "price",
            "bedrooms",
            "bathrooms",
            "area_sqft",
            "address",
            "point",
            "footprint",
            "similarity",
            "is_featured",
            "is_active",
            "created_at",
            "updated_at",
            "images",
            "distance",
        ]
