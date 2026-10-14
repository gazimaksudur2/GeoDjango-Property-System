from django.contrib.gis.db.models.functions import Distance
from django.core.paginator import Paginator
from django.shortcuts import render
from django.shortcuts import get_object_or_404

from .models import (
    Location,
    Property,
)


def home(request):
    return render(
        request,
        "home/index.html"
    )


def property_list(request):
    location_query = request.GET.get("location")

    properties = Property.objects.filter(
        is_active=True
    ).select_related(
        "location"
    ).prefetch_related(
        "images"
    )

    if location_query:
        location = Location.objects.filter(
            name__icontains=location_query
        ).first()

        if location:
            properties = properties.filter(
                location=location
            )

    paginator = Paginator(
        properties,
        6
    )

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "properties/listing.html",
        {
            "page_obj": page_obj,
            "location_query": location_query
        }
    )


def property_detail(request, slug):
    property = get_object_or_404(
        Property.objects
        .select_related("location")
        .prefetch_related("images")
        .annotate(
            city_distance=Distance(
                "point",
                "location__point"
            )
        ),
        slug=slug
    )

    amenities = [
        "Parking",
        "Security",
        "Balcony",
        "Garden"
    ]

    return render(
        request,
        "properties/detail.html",
        {
            "property": property,
            "amenities": amenities
        }
    )
