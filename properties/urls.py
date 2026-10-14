from django.urls import path
from . import views

urlpatterns = [

    path(
        "",
        views.property_list,
        name="property_list"
    ),

    path(
        "<slug:slug>/",
        views.property_detail,
        name="property_detail"
    ),
]
