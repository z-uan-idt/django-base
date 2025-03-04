from rest_framework.routers import DefaultRouter
from django.urls import path, include

from .views.user_view import APIUser
from .views.auth_view import APIAuth


v1_api_router = DefaultRouter(trailing_slash=False)
v1_api_router.register(prefix="user", viewset=APIUser, basename="user")
v1_api_router.register(prefix="auth", viewset=APIAuth, basename="auth")

users_urlpatterns = [
    path("api/v1/", include(v1_api_router.urls)),
]
