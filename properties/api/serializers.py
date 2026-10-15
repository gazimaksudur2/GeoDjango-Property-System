from rest_framework import serializers

from ..models import (
    Location,
    Property,
    PropertyImage,
)
import re


class AutocompleteQuerySerializer(serializers.Serializer):
    """Validates incoming autocomplete query parameters (Criterion 15)."""
    q = serializers.CharField(min_length=2, max_length=150, required=True)
    limit = serializers.IntegerField(min_value=1, max_value=20, default=8, required=False)

    def validate_q(self, value):
        cleaned = value.strip()
        if len(cleaned) < 2:
            raise serializers.ValidationError(
                "Query parameter 'q' must be at least 2 characters long."
            )
        if not re.match(r"^[a-zA-Z0-9\s,\-\.'\"&()/#:+|]+$", cleaned):
            raise serializers.ValidationError(
                "Query contains invalid special characters."
            )
        return cleaned


class DistanceField(serializers.Field):
    def to_representation(self, value):
        if value is None:
            return None
        return {
            "meters": round(value.m, 2),
            "kilometers": round(value.km, 3),
        }


class LocationSerializer(serializers.ModelSerializer):
    similarity = serializers.FloatField(read_only=True)

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

    def validate_name(self, value):
        cleaned = value.strip()
        if len(cleaned) < 2:
            raise serializers.ValidationError(
                "Location name must be at least 2 characters long."
            )
        return cleaned

    def validate_point(self, value):
        if value is not None:
            lng, lat = value.x, value.y
            if not (-180.0 <= lng <= 180.0 and -90.0 <= lat <= 90.0):
                raise serializers.ValidationError(
                    "Coordinates out of range. Longitude must be between"
                    + " -180 and 180, and latitude between -90 and 90."
                )
        return value


class PropertyAutocompleteSerializer(serializers.ModelSerializer):
    """Lightweight serializer for Property mode autocomplete dropdown."""
    location_name = serializers.CharField(source="location.name", read_only=True)
    city = serializers.CharField(source="location.city", read_only=True)
    similarity = serializers.FloatField(read_only=True)

    class Meta:
        model = Property
        fields = [
            "id",
            "title",
            "slug",
            "property_type",
            "price",
            "bedrooms",
            "location_name",
            "city",
            "similarity",
        ]


class PropertyImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyImage
        fields = [
            "id",
            "image",
            "caption",
            "alt_text",
            "is_primary",
            "sort_order",
        ]

    def validate_sort_order(self, value):
        if value < 0:
            raise serializers.ValidationError(
                "Sort order cannot be negative."
            )
        return value


class PropertySerializer(serializers.ModelSerializer):
    images = PropertyImageSerializer(
        many=True,
        read_only=True,
    )
    distance = DistanceField(read_only=True)
    similarity = serializers.FloatField(read_only=True)

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

    def validate_title(self, value):
        cleaned = value.strip()
        if len(cleaned) < 5:
            raise serializers.ValidationError(
                "Property title must be at least 5 characters long."
            )
        return cleaned

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Property price must be greater than zero."
            )
        return value

    def validate_area_sqft(self, value):
        if value is not None and value <= 0:
            raise serializers.ValidationError(
                "Property area in sqft must be greater than zero."
            )
        return value

    def validate(self, attrs):
        bedrooms = attrs.get("bedrooms", getattr(self.instance, "bedrooms", 0))
        bathrooms = attrs.get(
            "bathrooms",
            getattr(self.instance, "bathrooms", 0)
        )
        property_type = attrs.get(
            "property_type",
            getattr(self.instance, "property_type", ""),
        )
        point = attrs.get("point", getattr(self.instance, "point", None))

        if bedrooms < 0 or bathrooms < 0:
            raise serializers.ValidationError(
                "Bedrooms and bathrooms cannot be negative."
            )

        if property_type and property_type.lower() in {
            "apartment",
            "villa",
            "house"
        }:
            if bedrooms == 0:
                raise serializers.ValidationError(
                    {
                        "bedrooms":
                        f"A {property_type} must have at least 1 bedroom."
                    }
                )

        if point is not None:
            lng, lat = point.x, point.y
            if not (-180.0 <= lng <= 180.0 and -90.0 <= lat <= 90.0):
                raise serializers.ValidationError(
                    {
                        "point": "Invalid geographic coordinates provided."
                    }
                )

        return attrs