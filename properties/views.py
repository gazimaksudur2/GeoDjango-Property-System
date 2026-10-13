from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance

from .models import (
    Location,
    Property,
    PropertyImage,
)

from .serializers import (
    LocationSerializer,
    PropertySerializer,
    PropertyImageSerializer,
)


class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer


class PropertyViewSet(viewsets.ModelViewSet):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    filterset_fields = [
        "property_type",
        "status",
        "is_featured",
        "is_active",
        "bedrooms",
        "bathrooms",
    ]
    search_fields = [
        "title",
        "description",
        "address",
    ]
    ordering_fields = [
        "price",
        "created_at",
        "area_sqft",
    ]
    ordering = [
        "-created_at"
    ]

    @action(
        detail=False,
        methods=["get"]
    )
    def nearby(self, request):

        longitude = request.GET.get("lng")
        latitude = request.GET.get("lat")

        radius = request.GET.get(
            "radius",
            5
        )

        if not longitude or not latitude:
            return Response(
                {
                    "error": "lng and lat are required"
                },
                status=400
            )

        user_location = Point(
            float(longitude),
            float(latitude),
            srid=4326
        )

        properties = Property.objects.filter(
            point__distance_lte=(
                user_location,
                D(km=float(radius))
            )
        )

        serializer = PropertySerializer(
            properties,
            many=True
        )
        
        return Response(
            serializer.data
        )

    @action(
        detail=False,
        methods=["get"]
    )
    def nearest(self, request):

        longitude = request.GET.get("lng")
        latitude = request.GET.get("lat")

        if not longitude or not latitude:
            return Response(
                {
                    "error": "lng and lat are required"
                },
                status=400
            )

        user_location = Point(
            float(longitude),
            float(latitude),
            srid=4326
        )

        property_obj = (
            Property.objects
            .filter(point__isnull=False)
            .annotate(
                distance=Distance(
                    "point",
                    user_location
                )
            )
            .order_by(
                "distance"
            )
            .first()
        )

        if property_obj is None:
            return Response(
                {
                    "message": "No property found"
                },
                status=404
            )

        serializer = PropertySerializer(
            property_obj
        )

        return Response(
            serializer.data
        )

    @action(
        detail=False,
        methods=["get"]
    )
    def contains(self, request):
        longitude = request.GET.get("lng")
        latitude = request.GET.gt("lat")

        if not longitude or not latitude:
            return Response(
                {
                    "error": "lng and lat are required"
                },
                status=400
            )

        point = Point(
            float(longitude),
            float(latitude),
            srid=4326
        )

        properties = Property.objects.filter(
            footprint__contains=point
        )

        serializer = PropertySerializer(
            properties,
            many=True
        )
        
        return Response(
            serializer.data
        )


class PropertyImageViewSet(viewsets.ModelViewSet):
    queryset = PropertyImage.objects.all()
    serializer_class = PropertyImageSerializer
