from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from utils.decorators import singleton


@singleton
class APIMethod:

    def registry(self, method, url_path=None, detail=False, parsers=None,
                 permission_classes=None, authentication_classes=None, **kwargs):

        if authentication_classes is not None:
            kwargs["authentication_classes"] = authentication_classes
        if permission_classes is not None:
            kwargs["permission_classes"] = permission_classes
        if parsers:
            kwargs["parser_classes"] = parsers

        return action(
            detail=detail,
            methods=[method],
            url_path=url_path,
            **kwargs,
        )

    def post(self, url_path=None, authentication_classes=None,
             permission_classes=None, parsers=None, **kwargs):

        return self.registry(
            detail=False,
            method="post",
            parsers=parsers,
            url_path=url_path,
            permission_classes=permission_classes,
            authentication_classes=authentication_classes,
            **kwargs,
        )

    def put(self, url_path=None, authentication_classes=None,
            permission_classes=None, parsers=None, **kwargs):

        return self.registry(
            detail=True,
            method="put",
            parsers=parsers,
            url_path=url_path,
            permission_classes=permission_classes,
            authentication_classes=authentication_classes,
            **kwargs,
        )

    def get(self, url_path=None, detail=False,
            authentication_classes=None, permission_classes=None, **kwargs):

        return self.registry(
            parsers=None,
            method="get",
            detail=detail,
            url_path=url_path,
            permission_classes=permission_classes,
            authentication_classes=authentication_classes,
            **kwargs,
        )

    def delete(self, url_path=None, permission_classes=None,
               authentication_classes=None, **kwargs):

        return self.registry(
            detail=True,
            parsers=None,
            method="delete",
            url_path=url_path,
            permission_classes=permission_classes,
            authentication_classes=authentication_classes,
            **kwargs,
        )

    def patch(self, url_path=None, parsers=None,
              permission_classes=None, authentication_classes=None, **kwargs):

        return self.registry(
            detail=True,
            method="patch",
            parsers=parsers,
            url_path=url_path,
            permission_classes=permission_classes,
            authentication_classes=authentication_classes,
            **kwargs,
        )

    @property
    def swagger(self):
        return swagger_auto_schema


api = APIMethod()
