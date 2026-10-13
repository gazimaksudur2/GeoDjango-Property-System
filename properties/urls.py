from django.urls import path, include

from rest_framework.routers import DefaultRouter

from .views import (
    LocationViewSet,
    PropertyViewSet,
    PropertyImageViewSet,
)


router = DefaultRouter()

router.register(
    "locations",
    LocationViewSet
)

router.register(
    "properties",
    PropertyViewSet
)

router.register(
    "images",
    PropertyImageViewSet
)


urlpatterns = [
    path(
        "",
        include(router.urls)
    )
]