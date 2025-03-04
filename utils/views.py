from utils.mixins.base_api_view_mixin import BaseAPIViewMixin
from utils.mixins.serializer_mixin import GenericViewSetMixin
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins
from rest_framework import views


AUTO_SCHEMA_NONE = swagger_auto_schema(auto_schema=None)


@method_decorator(name="list", decorator=AUTO_SCHEMA_NONE)
@method_decorator(name="update", decorator=AUTO_SCHEMA_NONE)
@method_decorator(name="create", decorator=AUTO_SCHEMA_NONE)
@method_decorator(name="destroy", decorator=AUTO_SCHEMA_NONE)
@method_decorator(name="retrieve", decorator=AUTO_SCHEMA_NONE)
@method_decorator(name="partial_update", decorator=AUTO_SCHEMA_NONE)
class APIGenericView(BaseAPIViewMixin,
                     mixins.ListModelMixin,
                     mixins.CreateModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.DestroyModelMixin,
                     mixins.UpdateModelMixin,
                     GenericViewSetMixin):

    permission_classes = []
    permission_action_classes = {}

    def get_permissions(self):
        if self.action in self.permission_action_classes:
            actions = self.permission_action_classes[self.action]
            return [permission() for permission in actions]

        return [permission() for permission in self.permission_classes]

    def perform_create(self, serializer):
        return serializer.save()

    def perform_update(self, serializer):
        return serializer.save()


class APIView(BaseAPIViewMixin, views.APIView):

    pass
