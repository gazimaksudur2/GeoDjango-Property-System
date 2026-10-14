from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point

from pgvector.django import CosineDistance

from properties.models import Property
from properties.utils.embeddings import generate_embedding


def search_properties(
    query,
    latitude=None,
    longitude=None
):

    query_embedding = generate_embedding(
        query
    )

    properties = (
        Property.objects
        .filter(
            is_active=True
        )
        .annotate(
            similarity=CosineDistance(
                "embedding",
                query_embedding
            )
        )
        .order_by(
            "similarity"
        )
    )

    if latitude and longitude:

        user_point = Point(
            float(longitude),
            float(latitude),
            srid=4326
        )

        properties = (
            properties
            .annotate(
                distance=Distance(
                    "point",
                    user_point
                )
            )
            .order_by(
                "distance"
            )
        )

    return properties[:50]