from utils.mixins.serializer_mixin import SerializerMixin
from utils.mixins.serializer_mixin import EmptySerializer
from rest_framework.serializers import Serializer
from rest_framework.response import Response
from django.db.models.query import QuerySet
from utils.api_response import APIResponse
from utils.paginator import Paginator
from typing import Union, List


class BaseAPIViewMixin(SerializerMixin):

    @property
    def api_response(self):
        return APIResponse

    def get_request_serializer(self, *args, **kwargs) -> Union[type[Serializer], None]:
        if self.get_request_serializer_class():
            serializer_class = self.get_request_serializer_class()
        else:
            serializer_class = self.serializer_class

        if "context" not in kwargs:
            kwargs.setdefault("context", {})

        kwargs["context"].update(self.get_serializer_context() or {})

        return serializer_class(*args, **kwargs)

    def get_response_serializer(self, *args, **kwargs) -> Union[type[Serializer], None]:
        if self.get_response_serializer_class():
            serializer_class = self.get_response_serializer_class()
        else:
            serializer_class = self.serializer_class

        if "context" not in kwargs:
            kwargs.setdefault("context", {})

        kwargs["context"].update(self.get_serializer_context() or {})

        return serializer_class(*args, **kwargs)

    def get_serializer_class(self) -> Union[type[Serializer], None]:
        serializer_class = self.get_request_serializer_class()

        if serializer_class is None:
            serializer_class = self.serializer_class

        if serializer_class is None:
            setattr(self, "swagger_fake_view", True)
            serializer_class = EmptySerializer

        return serializer_class

    def initialize_request(self, request, *args, **kwargs):
        return super().initialize_request(request, *args, **kwargs)

    def finalize_response(self, request, response, *args, **kwargs):
        if not isinstance(response, Response):
            response = APIResponse(data=response)

        return super().finalize_response(request, response, *args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def handle_exception(self, exc):
        return super().handle_exception(exc)

    def paginator(self, object_list: Union[List, QuerySet],
                  per_page: int = None, page: int = None, **kwargs):

        response_serializer = self.get_response_serializer

        if page is None:
            page = Paginator.from_request(self.request, "page")

        if per_page is None:
            per_page = Paginator.from_request(self.request, "limit")

        _paginator = Paginator(object_list, per_page)
        _paginator = _paginator.page(page)
        _paginator = _paginator.set_results_classes(response_serializer,
                                                    option=kwargs)
        return _paginator.output_results
