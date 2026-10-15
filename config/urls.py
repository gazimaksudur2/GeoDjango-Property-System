from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

from properties.views import home


urlpatterns = [
    path(
        "admin/",
        admin.site.urls,
    ),
    path(
        "api/v1/",
        include("properties.api.urls"),
    ),
    path(
        "properties/",
        include("properties.urls"),
    ),
    path(
        "",
        home,
        name="home",
    ),
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )