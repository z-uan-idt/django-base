from drf_yasg.views import get_schema_view
from rest_framework import permissions
from django.views.static import serve
from django.contrib import admin
from django.conf import settings
from django.urls import re_path
from django.urls import path
from drf_yasg import openapi

from apps.user.urls import users_urlpatterns


schema_view = get_schema_view(
    openapi.Info(
        title="Backend Django Boilerplate",
        default_version="v1",
        description="Backend Django Boilerplate Documents",
        contact=openapi.Contact(email="chuong.kv@idtinc.co"),
        license=openapi.License(name="Copyright © 2025 by ChuongKV - IDT Inc"),
    ),
    permission_classes=(permissions.AllowAny,),
    authentication_classes=(),
    public=True,
)

swaggers_urlpatterns = [
    re_path(
        r"^swagger(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    re_path(
        r"^swagger/$|^swagger$",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    re_path(
        r"^redoc/$|^redoc$",
        schema_view.with_ui("redoc", cache_timeout=0),
        name="schema-redoc",
    ),
]


urlpatterns = [
    path("admin/", admin.site.urls),
    re_path(
        r"^media/(?P<path>.*)$",
        serve,
        {"document_root": settings.MEDIA_ROOT},
    ),
    re_path(
        r"^static/(?P<path>.*)$",
        serve,
        {"document_root": settings.STATIC_ROOT},
    ),
]

urlpatterns += swaggers_urlpatterns
urlpatterns += users_urlpatterns
