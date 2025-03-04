from constants.response_messages import ResponseMessage
from rest_framework.serializers import Serializer
from rest_framework.exceptions import NotFound
from rest_framework import viewsets
from typing import Dict


class EmptySerializer(Serializer):

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class SerializerMixin(object):
    request_serializer_class = None
    response_serializer_class = None
    action_serializers: Dict[str, Serializer] = {}

    def get_request_serializer_class(self):
        if self.action + "_request" in self.action_serializers:
            return self.action_serializers.get(self.action + "_request", None)

        if self.request_serializer_class:
            return self.request_serializer_class

        return self.serializer_class

    def get_response_serializer_class(self):
        if self.action + "_response" in self.action_serializers:
            return self.action_serializers.get(self.action + "_response", None)

        if self.response_serializer_class:
            return self.response_serializer_class

        return self.serializer_class


class GenericViewSetMixin(viewsets.GenericViewSet):
    action_query_sets = {}

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return None

        if self.action in self.action_query_sets:
            return self.action_query_sets.get(self.action, None)

        if getattr(self, "queryset", None) is not None:
            return super().get_queryset()

        raise NotFound(ResponseMessage.NOT_FOUND)
