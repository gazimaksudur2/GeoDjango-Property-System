from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    LocationViewSet,
    PropertyViewSet,
)

router = DefaultRouter()

router.register(
    "locations",
    LocationViewSet,
    basename="location"
)

router.register(
    "properties",
    PropertyViewSet,
    basename="property"
)

urlpatterns = [
    path(
        "",
        include(router.urls)
    ),
]
