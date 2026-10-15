from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from pgvector.django import CosineDistance

from properties.models import Property
from properties.utils.embeddings import generate_embedding


def search_properties(
    query,
    latitude=None,
    longitude=None,
    radius_km=10.0,
):
    query_embedding = generate_embedding(query)

    properties = (
        Property.objects.filter(
            is_active=True,
            embedding__isnull=False,
        )
        .select_related("location")
        .prefetch_related("images")
        .annotate(
            similarity=CosineDistance(
                "embedding",
                query_embedding,
            )
        )
    )

    if latitude is not None and longitude is not None:
        user_point = Point(
            float(longitude),
            float(latitude),
            srid=4326,
        )

        properties = (
            properties.filter(
                point__dwithin=(
                    user_point,
                    D(km=float(radius_km)),
                )
            )
            .annotate(
                distance=Distance(
                    "point",
                    user_point,
                )
            )
            .order_by("similarity", "distance")
        )
    else:
        properties = properties.order_by("similarity")

    return properties[:50]