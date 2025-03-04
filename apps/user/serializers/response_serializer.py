from rest_framework_simplejwt.tokens import RefreshToken
from constants.response_messages import ResponseMessage
from helpers.token_helper import TokenHelper
from utils.exception import MessageError
from rest_framework import serializers


from ..models.utils.choices import UserStatusChoices
from ..services.user_service import UserService
from ..models.user import User


class AuthenticationUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ("id", "username", "fullname", "status")
        service = UserService()

    def to_representation(self, instance):
        status = UserStatusChoices(instance.status)
        repr = super().to_representation(instance)
        repr["status_label"] = status.label
        repr["status_name"] = status.name
        repr["status"] = repr.pop("status")
        return repr


class AuthenticationSerializer(serializers.Serializer):

    helper = TokenHelper()

    def to_representation(self, instance):
        refresh_token = RefreshToken.for_user(instance)

        output, _ = self.helper.generate(
            user=AuthenticationUserSerializer(instance).data,
            refresh_token=refresh_token,
        )
        return output


class TokenSerializer(serializers.Serializer):

    helper = TokenHelper()

    def to_representation(self, instance):
        token_type = instance["token_type"]
        token = instance["token"]

        if token_type == "refresh_token":
            refresh_token = RefreshToken(token)
            output, user = self.helper.generate(refresh_token=refresh_token)
            output["user"] = AuthenticationUserSerializer(user).data
            return output

        raise MessageError(ResponseMessage.BAD_REQUEST)


class ShortUserDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "fullname", "created_at", "status")

    def to_representation(self, instance):
        status = UserStatusChoices(instance.status)
        repr = super().to_representation(instance)
        repr["status_label"] = status.label
        repr["status_name"] = status.name
        repr["status"] = repr.pop("status")
        return repr


class UserDetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ("id", "username", "fullname",
                  "created_at", "is_superuser", "status")
        service = UserService()

    def to_representation(self, instance):
        status = UserStatusChoices(instance.status)
        repr = super().to_representation(instance)
        repr["status_label"] = status.label
        repr["status_name"] = status.name
        repr["status"] = repr.pop("status")
        return repr
