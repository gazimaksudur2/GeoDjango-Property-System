from django.contrib import admin
from django.contrib.gis.admin import GISModelAdmin
from django.utils.html import format_html

from .models import Location, Property, PropertyImage


class PriceRangeFilter(admin.SimpleListFilter):
    title = "Price Range"
    parameter_name = "price_range"

    def lookups(self, request, model_admin):
        return [
            ("budget", "Budget (< 50,000)"),
            ("mid", "Mid-Range (50,000 - 200,000)"),
            ("luxury", "Luxury (> 200,000)"),
        ]

    def queryset(self, request, queryset):
        if self.value() == "budget":
            return queryset.filter(price__lt=50000)
        if self.value() == "mid":
            return queryset.filter(price__gte=50000, price__lte=200000)
        if self.value() == "luxury":
            return queryset.filter(price__gt=200000)
        return queryset


class EmbeddingStatusFilter(admin.SimpleListFilter):
    title = "AI Embedding Status"
    parameter_name = "has_embedding"

    def lookups(self, request, model_admin):
        return [
            ("yes", "Generated"),
            ("no", "Missing"),
        ]

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.filter(embedding__isnull=False)
        if self.value() == "no":
            return queryset.filter(embedding__isnull=True)
        return queryset


class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1
    readonly_fields = ("image_preview", "created_at")
    fields = (
        "image",
        "image_preview",
        "alt_text",
        "caption",
        "is_primary",
        "sort_order",
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 80px; max-width: 120px; '
                'object-fit: cover; border-radius: 6px; border: 1px solid #ddd;" />',
                obj.image.url,
            )
        return "No image uploaded"

    image_preview.short_description = "Preview"


@admin.register(Location)
class LocationAdmin(GISModelAdmin):
    list_display = (
        "name",
        "city",
        "state",
        "country",
        "is_active",
        "has_embedding",
    )
    list_filter = (
        "country",
        "state",
        "city",
        "is_active",
        EmbeddingStatusFilter,
    )
    search_fields = (
        "name",
        "city",
        "state",
        "country",
        "address",
    )
    prepopulated_fields = {"slug": ("name",)}

    @admin.display(boolean=True, description="Embedding")
    def has_embedding(self, obj):
        return obj.embedding is not None


@admin.register(Property)
class PropertyAdmin(GISModelAdmin):
    list_display = (
        "thumbnail_preview",
        "title",
        "location",
        "property_type",
        "status",
        "price",
        "bedrooms",
        "is_featured",
        "is_active",
    )
    list_display_links = ("thumbnail_preview", "title")
    list_filter = (
        PriceRangeFilter,
        EmbeddingStatusFilter,
        "property_type",
        "status",
        "bedrooms",
        "is_featured",
        "is_active",
        "location__city",
    )
    search_fields = (
        "title",
        "description",
        "address",
        "location__name",
        "location__city",
    )
    prepopulated_fields = {"slug": ("title",)}
    inlines = [PropertyImageInline]

    def thumbnail_preview(self, obj):
        first_image = obj.images.first()
        if first_image and first_image.image:
            return format_html(
                '<img src="{}" style="width: 50px; height: 40px; '
                'object-fit: cover; border-radius: 4px;" />',
                first_image.image.url,
            )
        return "—"

    thumbnail_preview.short_description = "Image"


@admin.register(PropertyImage)
class PropertyImageAdmin(admin.ModelAdmin):
    list_display = (
        "image_preview",
        "property",
        "is_primary",
        "sort_order",
        "created_at",
    )
    list_filter = ("is_primary", "created_at")
    search_fields = ("property__title", "caption", "alt_text")
    readonly_fields = ("image_preview",)

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 60px; max-width: 90px; '
                'object-fit: cover; border-radius: 4px;" />',
                obj.image.url,
            )
        return "No image"

    image_preview.short_description = "Preview"
