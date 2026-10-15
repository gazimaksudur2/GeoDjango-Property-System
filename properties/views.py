from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D
from django.core.paginator import Paginator
from django.db.models import Case, IntegerField, Q, Value, When
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from pgvector.django import CosineDistance

from .forms import PropertySearchForm
from .models import Location, Property
from .utils.embeddings import generate_embedding


def home(request):
    form = PropertySearchForm(initial={"search_type": "location"})
    return render(
        request,
        "home/index.html",
        {"form": form, "search_type": "location"},
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
    search_type = request.GET.get("search_type", "location")
    if search_type not in {"location", "property"}:
        search_type = "location"

    matched_location = None
    matched_property = None
    anchor_label = ""

    if form.is_valid():
        search_type = form.cleaned_data.get("search_type") or "location"
        target_id = form.cleaned_data.get("target_id")
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

            if search_type == "location":
                if target_id:
                    matched_location = Location.objects.filter(
                        id=target_id, is_active=True
                    ).first()

                if not matched_location:
                    matched_location = Location.objects.filter(
                        Q(name__icontains=location_query)
                        | Q(city__icontains=location_query),
                        is_active=True,
                    ).first()

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
                        .filter(loc_similarity__lte=0.55)
                        .order_by("loc_similarity")
                        .first()
                    )

                if matched_location and matched_location.point:
                    anchor_label = matched_location.name
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
                        .order_by("search_distance", "similarity")
                    )
                else:
                    properties = Property.objects.none()

            elif search_type == "property":
                properties = (
                    properties.filter(embedding__isnull=False)
                    .annotate(
                        similarity=CosineDistance(
                            "embedding",
                            query_embedding,
                        ),
                        exact_boost=Case(
                            When(id=target_id, then=Value(0))
                            if target_id
                            else When(pk__isnull=True, then=Value(0)),
                            When(title__icontains=location_query, then=Value(1)),
                            default=Value(2),
                            output_field=IntegerField(),
                        ),
                    )
                    .filter(
                        Q(id=target_id)
                        | Q(title__icontains=location_query)
                        | Q(description__icontains=location_query)
                        | Q(property_type__icontains=location_query)
                        | Q(similarity__lte=0.68)
                        if target_id
                        else (
                            Q(title__icontains=location_query)
                            | Q(description__icontains=location_query)
                            | Q(property_type__icontains=location_query)
                            | Q(similarity__lte=0.68)
                        )
                    )
                    .order_by("exact_boost", "similarity")
                )

                if target_id:
                    matched_property = Property.objects.filter(
                        id=target_id, is_active=True
                    ).first()
                if not matched_property:
                    matched_property = properties.first()

                if matched_property and matched_property.point:
                    anchor_label = matched_property.title
                    properties = properties.annotate(
                        search_distance=Distance(
                            "point",
                            matched_property.point,
                        )
                    ).order_by("exact_boost", "similarity", "search_distance")
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
            "search_type": search_type,
            "matched_location": matched_location,
            "matched_property": matched_property,
            "anchor_label": anchor_label,
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

    nearby_properties = []
    if property_obj.point:
        nearby_properties = (
            Property.objects.filter(is_active=True, point__isnull=False)
            .exclude(id=property_obj.id)
            .select_related("location")
            .prefetch_related("images")
            .annotate(
                city_distance=Distance("point", "location__point"),
                search_distance=Distance("point", property_obj.point),
            )
            .order_by("search_distance")[:3]
        )

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
            "nearby_properties": nearby_properties,
            "anchor_label": property_obj.title,
            "back_url": back_url,
        },
    )
