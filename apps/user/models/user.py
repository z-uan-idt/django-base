from django.contrib.auth.models import AbstractBaseUser
from utils.base_models import BaseModelSoftDelete
from django.db import models

from ..models.utils.choices import UserStatusChoices
from ..models.utils.manager import UserManager


class User(AbstractBaseUser, BaseModelSoftDelete):
    fullname = models.CharField(max_length=255, null=True, blank=True)
    username = models.CharField(max_length=255, unique=True)
    is_superuser = models.BooleanField(default=False)
    password = models.CharField(max_length=255)
    status = models.IntegerField(
        choices=UserStatusChoices.choices,
        default=UserStatusChoices.ACTIVE,
    )
    created_by = models.ForeignKey(
        "self",
        null=True,
        on_delete=models.SET_NULL,
        related_name="User_created_by",
    )

    last_login = None

    REQUIRED_FIELDS = ["fullname"]
    USERNAME_FIELD = "username"

    @property
    def is_staff(self):
        return self.is_superuser

    objects = UserManager()

    class Meta:
        db_table = "users_user"
        verbose_name = "Tài khoản"
        verbose_name_plural = "Quản lý tài khoản"
        indexes = [
            models.Index(fields=["username"]),
            models.Index(fields=["created_by"]),
            models.Index(fields=["created_at"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return "{}: {} | {}".format(self.id, self.username, self.fullname)

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True
