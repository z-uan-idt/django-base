from constants.response_messages import ResponseMessage
from utils.exception import MessageError
from rest_framework import serializers

from ..services.user_service import UserService
from ..models.utils.choices import UserStatusChoices


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        user_service = UserService()
        username = str(attrs["username"]).lower()

        try:
            self.user = user_service.get_user_with_username(username=username,
                                                            is_deleted=False)
        except:
            raise MessageError(ResponseMessage.INVALID_USERNAME)

        if not self.user.check_password(attrs["password"]):
            raise MessageError(ResponseMessage.INVALID_PASSWORD)

        if self.user.status == UserStatusChoices.BANNED:
            raise MessageError(ResponseMessage.USER_BANNED)

        return super().validate(attrs)


class TokenSerializer(serializers.Serializer):
    token = serializers.CharField(required=True,
                                  allow_null=False,
                                  allow_blank=False)
    token_type = serializers.ChoiceField(
        required=True,
        allow_null=False,
        allow_blank=False,
        choices=(("refresh_token", "Refresh Token"),
                 ("access_token", "Access Token")),
    )
