from django.db import models


class UserStatusChoices(models.IntegerChoices):
    PENDING = 1, "Chờ xác nhận"
    ACTIVE = 2, "Đang hoạt động"
    SUSPENDED = 3, "Tạm ngừng hoạt động"
    BANNED = 4, "Đang bị khoá"
