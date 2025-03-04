from rest_framework.permissions import IsAuthenticated
from utils.views import APIGenericView
from utils.decorators import api

from ..serializers import request_serializer
from ..serializers import response_serializer

from ..docs import auth_swagger


class APIAuth(APIGenericView):
    action_serializers = {
        "login_request": request_serializer.LoginSerializer,
        "login_response": response_serializer.AuthenticationSerializer,
        "token_request": request_serializer.TokenSerializer,
        "token_response": response_serializer.TokenSerializer,
        "profile_response": response_serializer.UserDetailsSerializer,
    }

    permission_action_classes = {
        "profile": [IsAuthenticated],
    }

    @api.swagger(
        tags=["Auth"],
        operation_id="Auth Login",
    )
    @api.post(authentication_classes=[])
    def login(self, request, *args, **kwargs):
        serializer = self.get_request_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return self.api_response(
            data=self.get_response_serializer(serializer.user).data,
            message="Đăng nhập thành công",
        )

    @api.swagger(
        tags=["Auth"],
        operation_id="Auth Token",
        manual_parameters=[
            auth_swagger.TOKEN_PARAMETER,
            auth_swagger.TOKEN_TYPE_PARAMETER, 
        ],
    )
    @api.get(authentication_classes=[])
    def token(self, request, *args, **kwargs):
        serializer = self.get_request_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        return self.get_response_serializer(serializer.validated_data).data

    @api.get()
    @api.swagger(
        tags=["Auth"],
        operation_id="Auth Profile",
    )
    def profile(self, request):
        return self.get_response_serializer(request.user).data
