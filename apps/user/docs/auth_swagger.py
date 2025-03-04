from drf_yasg import openapi


TOKEN_PARAMETER = openapi.Parameter(
    name="token",
    required=True,
    in_=openapi.IN_QUERY,
    type=openapi.TYPE_STRING,
    description="Access Token",
)

REFRESH_TOKEN_PARAMETER = openapi.Parameter(
    required=True,
    name="refresh_token",
    in_=openapi.IN_QUERY,
    type=openapi.TYPE_STRING,
    description="Refresh Token",
)


TOKEN_TYPE_PARAMETER = openapi.Parameter(
    required=True,
    name="token_type",
    in_=openapi.IN_QUERY,
    type=openapi.TYPE_STRING,
    description="type: [access_token, refresh_token]",
)