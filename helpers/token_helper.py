from rest_framework_simplejwt.tokens import RefreshToken
from utils.decorators import singleton
from django.conf import settings
from typing import Any


from apps.user.services.user_service import UserService


@singleton
class TokenHelper:
    user_service = UserService()

    @property
    def tokenexpiry(self):
        SIMPLE_JWT = getattr(settings, "SIMPLE_JWT", {})
        AUTH_HEADER_TYPES = SIMPLE_JWT.get("AUTH_HEADER_TYPES") or []
        ACCESS_TOKEN_LIFETIME = SIMPLE_JWT.get("ACCESS_TOKEN_LIFETIME")

        expires_in = 0

        if hasattr(ACCESS_TOKEN_LIFETIME, "total_seconds"):
            expires_in = ACCESS_TOKEN_LIFETIME.total_seconds()

        token_type = AUTH_HEADER_TYPES[0] if len(
            AUTH_HEADER_TYPES) > 0 else None

        return expires_in, token_type, "seconds"

    def generate(self, refresh_token: RefreshToken, user: Any = None):
        _expires_in, _token_type, _expires_type = self.tokenexpiry

        instance = {
            "access_token": str(refresh_token.access_token),
            "refresh_token": str(refresh_token),
            "expires_type": _expires_type,
            "token_type": _token_type,
            "expires_in": _expires_in,
        }

        if user is not None:
            instance["user"] = user

        user_id = refresh_token.access_token.get("user_id")

        return instance, self.user_service.get_user_with_id(user_id)
