from django.contrib import admin

from .models import (
    Location,
    Property,
    PropertyImage,
)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "country",
        "state",
        "city",
        "is_active",
    )

    search_fields = (
        "name",
        "city",
        "country",
    )


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "property_type",
        "status",
        "price",
        "is_featured",
        "is_active",
    )

    list_filter = (
        "property_type",
        "status",
        "is_featured",
        "is_active",
    )

    search_fields = (
        "title",
        "description",
    )


@admin.register(PropertyImage)
class PropertyImageAdmin(admin.ModelAdmin):
    list_display = (
        "property",
        "is_primary",
        "sort_order",
        "created_at",
    )

    list_filter = (
        "is_primary",
    )