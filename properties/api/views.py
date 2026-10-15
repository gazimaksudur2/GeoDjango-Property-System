from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance
from django.db.models import Q
from pgvector.django import CosineDistance
from properties.utils.embeddings import generate_embedding

from ..models import (
    Location,
    Property,
)

from .serializers import (
    AutocompleteQuerySerializer,
    LocationSerializer,
    PropertyAutocompleteSerializer,
    PropertySerializer,
)


class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer

    @action(detail=False, methods=["get"])
    def semantic_search(self, request):
        query = request.GET.get("q")
        if not query:
            return Response({"error": "q parameter is required"}, status=400)

        query_embedding = generate_embedding(query)
        locations = (
            Location.objects.filter(embedding__isnull=False)
            .annotate(similarity=CosineDistance("embedding", query_embedding))
            .order_by("similarity")[:10]
        )
        serializer = LocationSerializer(locations, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def autocomplete(self, request):
        """Fires when the frontend search toggle is set to 'Location'."""
        query = request.GET.get("q", "").strip()
        if len(query) < 2:
            return Response([])

        query_serializer = AutocompleteQuerySerializer(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)
        cleaned_query = query_serializer.validated_data["q"]
        limit = query_serializer.validated_data["limit"]

        results = []
        seen_ids = set()

        exact_locations = Location.objects.filter(
            Q(name__icontains=cleaned_query) | Q(city__icontains=cleaned_query),
            is_active=True,
        )[:5]

        for loc_data in LocationSerializer(exact_locations, many=True).data:
            seen_ids.add(loc_data["id"])
            results.append(loc_data)

        query_embedding = generate_embedding(cleaned_query)
        semantic_locations = (
            Location.objects.filter(embedding__isnull=False, is_active=True)
            .exclude(id__in=seen_ids)
            .annotate(similarity=CosineDistance("embedding", query_embedding))
            .order_by("similarity")[:limit]
        )

        for loc_data in LocationSerializer(semantic_locations, many=True).data:
            if loc_data["id"] not in seen_ids:
                seen_ids.add(loc_data["id"])
                results.append(loc_data)

        return Response(results[:limit])


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
    ordering = ["-created_at"]

    @action(detail=False, methods=["get"])
    def autocomplete(self, request):
        """Fires when the frontend search toggle is set to 'Property'."""
        query = request.GET.get("q", "").strip()
        if len(query) < 2:
            return Response([])

        query_serializer = AutocompleteQuerySerializer(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)
        cleaned_query = query_serializer.validated_data["q"]
        limit = query_serializer.validated_data["limit"]

        results = []
        seen_ids = set()

        exact_properties = (
            Property.objects.select_related("location")
            .filter(
                Q(title__icontains=cleaned_query)
                | Q(property_type__icontains=cleaned_query),
                is_active=True,
            )[:4]
        )

        for prop_data in PropertyAutocompleteSerializer(exact_properties, many=True).data:
            seen_ids.add(prop_data["id"])
            results.append(prop_data)

        query_embedding = generate_embedding(cleaned_query)
        semantic_properties = (
            Property.objects.select_related("location")
            .filter(embedding__isnull=False, is_active=True)
            .exclude(id__in=seen_ids)
            .annotate(similarity=CosineDistance("embedding", query_embedding))
            .order_by("similarity")[:limit]
        )

        for prop_data in PropertyAutocompleteSerializer(semantic_properties, many=True).data:
            if prop_data["id"] not in seen_ids:
                seen_ids.add(prop_data["id"])
                results.append(prop_data)

        return Response(results[:limit])

    @action(detail=False, methods=["get"])
    def nearby(self, request):
        longitude = request.GET.get("lng")
        latitude = request.GET.get("lat")
        radius = request.GET.get("radius", 5)

        if not longitude or not latitude:
            return Response({"error": "lng and lat are required"}, status=400)

        user_location = Point(float(longitude), float(latitude), srid=4326)
        properties = Property.objects.filter(
            point__distance_lte=(user_location, D(km=float(radius)))
        )
        serializer = PropertySerializer(properties, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def nearest(self, request):
        longitude = request.GET.get("lng")
        latitude = request.GET.get("lat")

        if not longitude or not latitude:
            return Response({"error": "lng and lat are required"}, status=400)

        user_location = Point(float(longitude), float(latitude), srid=4326)
        property_obj = (
            Property.objects.filter(point__isnull=False)
            .annotate(distance=Distance("point", user_location))
            .order_by("distance")
            .first()
        )

        if property_obj is None:
            return Response({"message": "No property found"}, status=404)

        serializer = PropertySerializer(property_obj)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def contains(self, request):
        longitude = request.GET.get("lng")
        latitude = request.GET.get("lat")

        if not longitude or not latitude:
            return Response({"error": "lng and lat are required"}, status=400)

        point = Point(float(longitude), float(latitude), srid=4326)
        properties = Property.objects.filter(footprint__contains=point)
        serializer = PropertySerializer(properties, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def semantic_search(self, request):
        query = request.GET.get("q")
        if not query:
            return Response({"error": "q parameter is required"}, status=400)

        query_embedding = generate_embedding(query)
        properties = (
            Property.objects.filter(embedding__isnull=False)
            .annotate(similarity=CosineDistance("embedding", query_embedding))
            .order_by("similarity")[:10]
        )
        serializer = PropertySerializer(properties, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def hybrid_search(self, request):
        query = request.GET.get("q")
        longitude = request.GET.get("lng")
        latitude = request.GET.get("lat")
        user_location = None
        radius = request.GET.get("radius", 5)

        if not query:
            return Response({"error": "q parameter is required"}, status=400)

        query_embedding = generate_embedding(query)
        properties = Property.objects.filter(embedding__isnull=False)

        if longitude and latitude:
            user_location = Point(float(longitude), float(latitude), srid=4326)
            properties = properties.filter(
                point__distance_lte=(user_location, D(km=float(radius)))
            )

        properties = properties.annotate(
            similarity=CosineDistance("embedding", query_embedding)
        )

        if user_location:
            properties = properties.annotate(
                distance=Distance("point", user_location)
            )

        properties = properties.order_by("similarity")[:10]
        serializer = PropertySerializer(properties, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def location_hybrid_search(self, request):
        query = request.GET.get("q")
        if not query:
            return Response({"error": "q parameter is required"}, status=400)

        query_embedding = generate_embedding(query)
        locations = (
            Location.objects.filter(embedding__isnull=False)
            .annotate(similarity=CosineDistance("embedding", query_embedding))
            .order_by("similarity")[:3]
        )

        if not locations.exists():
            return Response({"message": "No matching location found"}, status=404)

        location = locations.first()
        properties = (
            Property.objects.filter(location=location, embedding__isnull=False)
            .annotate(similarity=CosineDistance("embedding", query_embedding))
            .order_by("similarity")[:10]
        )
        serializer = PropertySerializer(properties, many=True)
        return Response(
            {
                "location": location.name,
                "properties": serializer.data,
            }
        )