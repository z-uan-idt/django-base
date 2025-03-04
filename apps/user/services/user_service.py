from utils.exception import MessageError
from utils.decorators import singleton
from django.db import models

from ..models import User


@singleton
class UserService:
    user_objects = User.objects

    def get_users(self, keyword=None, status=None, **kwargs):
        filter_query = models.Q()

        if status is not None:
            filter_query &= models.Q(status=status)

        if keyword not in (None, ""):
            search_query = models.Q(username__icontains=keyword)
            search_query |= models.Q(fullname__icontains=keyword)
            filter_query &= search_query

        users = self.user_objects.filter(filter_query)

        order_by = str(kwargs.get("order_by") or "asc").lower()

        if order_by == "asc":
            users = users.order_by("created_at")
        else:
            users = users.order_by("-created_at")

        return users

    def get_user_with_id(self, id: int, **kwargs):
        return self.user_objects.get(pk=id, **kwargs)

    def get_user_with_username(self, username: str, **kwargs):
        username_field = User.USERNAME_FIELD
        filter_kwargs = {username_field: username}
        filter_kwargs.update(kwargs)
        return self.user_objects.get(**filter_kwargs)

    def user_exists(self, username: str):
        username_field = User.USERNAME_FIELD
        filter_kwargs = {username_field: username}
        return self.user_objects.filter(**filter_kwargs).exists()

    def delete_user(self, id: int):
        user = self.get_user_with_id(id)
        user.delete()

    def create_user(self, **kwargs):
        password = kwargs.pop("password", None)
        is_register = kwargs.pop("is_register", False)

        if not password:
            raise MessageError("Mật khẩu không được phép bỏ trống")

        instance = self.user_objects.create(**kwargs)
        instance.set_password(password)

        if is_register:
            instance.created_by = instance

        instance.save()

        return instance

    def update_user(self, instance: User, **kwargs):
        instance.fullname = kwargs.get("fullname", instance.fullname)
        instance.status = kwargs.get("status", instance.status)
        instance.save()

        return instance
