from rest_framework import serializers

from .models import (
    Location,
    Property,
    PropertyImage,
)


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = "__all__"


class PropertyImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = PropertyImage
        fields = "__all__"


class PropertySerializer(serializers.ModelSerializer):
    images = PropertyImageSerializer(
        many=True,
        read_only=True
    )

    distance = serializers.FloatField(read_only=True)

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
            "embedding",
            "is_featured",
            "is_active",
            "created_at",
            "updated_at",
            "images",
            "distance",
        ]
