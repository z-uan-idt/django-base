from django.utils.functional import cached_property
from django.utils.inspect import method_has_no_args
from django.db.models.query import QuerySet
from rest_framework.request import Request
from typing import Union
import inspect
import math


class Paginator:
    DEFAULT_PAGE = 1
    DEFAULT_PER_PAGE = 10

    def __init__(self, object_list: Union[list, QuerySet], per_page: int = 10):
        if per_page < 1:
            raise ValueError("per_page must be at least 1")

        self._object_list = object_list
        self.per_page = per_page

    @staticmethod
    def from_request(request: Request, key: str = "page"):
        page_value = request.query_params.get(key) or request.data.get(key)

        if not page_value and key == "page":
            page_value = Paginator.DEFAULT_PAGE
        elif not page_value and key == "limit":
            page_value = Paginator.DEFAULT_PER_PAGE

        try:
            return int(page_value)
        except ValueError:
            raise ValueError(f"{key} must be an integer")

    def page(self, page: int = 1):
        if page < 1:
            raise ValueError("Page number must be at least 1")

        self.current_page = page
        current_page_index = page - 1

        self.bottom = current_page_index * self.per_page
        self.top = min(self.per_page + self.bottom, self.count)

        if page > self.num_pages and self.num_pages > 0:
            raise ValueError(f"Maximum page number is {self.num_pages}")

        return self

    def set_results_classes(self, classes: object, option: dict = {}):
        self.option_classes = option
        self.classes = classes
        return self

    @cached_property
    def num_pages(self):
        return math.ceil(self.count / self.per_page)

    @cached_property
    def count(self):
        count_method = getattr(self._object_list, "count", None)
        if (
            callable(count_method)
            and not inspect.isbuiltin(count_method)
            and method_has_no_args(count_method)
        ):
            return count_method()
        return len(self._object_list)

    @cached_property
    def object_results(self):
        return self._object_list[self.bottom: self.top]

    @cached_property
    def results(self):
        if hasattr(self, "classes"):
            kwargs = {"many": True}
            if hasattr(self, "option_classes"):
                kwargs.update(self.option_classes)
            return self.classes(self.object_results, **kwargs).data

        if hasattr(self.object_results, "values"):
            return list(self.object_results.values())

        return self.object_results

    @cached_property
    def output_results(self):
        return {"count": self.count,
                "num_pages": self.num_pages,
                "current_page": self.current_page,
                "previous_page": self.previous_page,
                "next_page": self.next_page,
                "per_page": self.per_page,
                "results": self.results}

    def get_output_results(self, results: list):
        return {"count": self.count,
                "num_pages": self.num_pages,
                "current_page": self.current_page,
                "previous_page": self.previous_page,
                "next_page": self.next_page,
                "per_page": self.per_page,
                "results": results}

    @cached_property
    def previous_page(self):
        return self.current_page - 1 if self.current_page > 1 else None

    @cached_property
    def next_page(self):
        return self.current_page + 1 if self.current_page < self.num_pages else None
