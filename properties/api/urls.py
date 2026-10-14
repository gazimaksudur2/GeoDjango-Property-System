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
    LocationViewSet,
    basename="location"
)

router.register(
    "properties",
    PropertyViewSet,
    basename="property"
)

router.register(
    "images",
    PropertyImageViewSet,
    basename="image"
)

urlpatterns = [

    path(
        "",
        include(router.urls)
    ),

]