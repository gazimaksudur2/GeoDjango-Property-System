from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, render
from pgvector.django import CosineDistance

from .forms import PropertySearchForm
from .models import Location, Property
from .utils.embeddings import generate_embedding
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme


def home(request):
    form = PropertySearchForm()
    return render(
        request,
        "home/index.html",
        {"form": form},
    )


def property_list(request):
    form = PropertySearchForm(request.GET or None)

    properties = (
        Property.objects.filter(is_active=True)
        .select_related("location")
        .prefetch_related("images")
        .annotate(city_distance=Distance("point", "location__point"))
    )

    location_query = ""
    matched_location = None

    if form.is_valid():
        location_query = form.cleaned_data.get("location")
        radius_km = form.cleaned_data.get("radius") or 10.0
        min_price = form.cleaned_data.get("min_price")
        max_price = form.cleaned_data.get("max_price")
        bedrooms = form.cleaned_data.get("bedrooms")

        if min_price is not None:
            properties = properties.filter(price__gte=min_price)

        if max_price is not None:
            properties = properties.filter(price__lte=max_price)

        if bedrooms is not None:
            properties = properties.filter(bedrooms__gte=bedrooms)

        if location_query:
            query_embedding = generate_embedding(location_query)

            matched_location = (
                Location.objects.filter(
                    Q(name__icontains=location_query)
                    | Q(city__icontains=location_query),
                    is_active=True,
                ).first()
            )

            if not matched_location:
                matched_location = (
                    Location.objects.filter(
                        embedding__isnull=False,
                        is_active=True,
                    )
                    .annotate(
                        loc_similarity=CosineDistance(
                            "embedding",
                            query_embedding,
                        )
                    )
                    .order_by("loc_similarity")
                    .first()
                )

            if matched_location and matched_location.point:
                properties = (
                    properties.filter(
                        Q(
                            point__dwithin=(
                                matched_location.point,
                                D(km=radius_km),
                            )
                        )
                        | Q(location=matched_location)
                    )
                    .annotate(
                        search_distance=Distance(
                            "point",
                            matched_location.point,
                        ),
                        similarity=CosineDistance(
                            "embedding",
                            query_embedding,
                        ),
                    )
                    .order_by("similarity", "search_distance")
                )
            else:
                properties = (
                    properties.filter(embedding__isnull=False)
                    .annotate(
                        similarity=CosineDistance(
                            "embedding",
                            query_embedding,
                        )
                    )
                    .order_by("similarity")
                )
        else:
            properties = properties.order_by("-is_featured", "-created_at")
    else:
        properties = properties.order_by("-is_featured", "-created_at")

    paginator = Paginator(properties, 6)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    query_params = request.GET.copy()
    if "page" in query_params:
        del query_params["page"]

    return render(
        request,
        "properties/listing.html",
        {
            "form": form,
            "page_obj": page_obj,
            "location_query": location_query,
            "matched_location": matched_location,
            "query_string": query_params.urlencode(),
        },
    )


def property_detail(request, slug):
    property_obj = get_object_or_404(
        Property.objects.select_related("location")
        .prefetch_related("images")
        .annotate(city_distance=Distance("point", "location__point")),
        slug=slug,
    )

    amenities = [
        "Parking",
        "Security",
        "Balcony",
        "Garden",
    ]

    base_list_url = reverse("property_list")
    query_string = request.GET.urlencode()
    referer = request.META.get("HTTP_REFERER", "")

    if query_string:
        back_url = f"{base_list_url}?{query_string}"
    elif referer and url_has_allowed_host_and_scheme(
        url=referer,
        allowed_hosts={request.get_host()},
    ):
        back_url = referer
    else:
        back_url = base_list_url

    return render(
        request,
        "properties/detail.html",
        {
            "property": property_obj,
            "amenities": amenities,
            "back_url": back_url,
        },
    )
