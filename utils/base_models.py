from django_currentuser.middleware import get_current_user
from constants.response_messages import ResponseMessage
from django.contrib.auth.models import AnonymousUser
from utils.exception import MessageError
from django.utils import timezone
from django.db import models


class BaseModel(models.Model):
    modified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if self.pk is not None:
            self.modified_at = timezone.now()

        if hasattr(self, "created_by"):
            user = get_current_user()

            if user and user != AnonymousUser() and self.created_by is None:
                setattr(self, "created_by", user)

        if hasattr(self, "updated_by"):
            user = get_current_user()

            if user and user != AnonymousUser() and self.updated_by is None:
                setattr(self, "updated_by", user)

        super(BaseModel, self).save(*args, **kwargs)


class BaseModelSoftDelete(BaseModel):
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False, hard_delete=False):

        if hard_delete:
            super(BaseModelSoftDelete, self).delete(using, keep_parents)
            return

        if self.is_deleted:
            raise MessageError(ResponseMessage.DELETED_ERROR)

        self.deleted_at = timezone.now()
        self.is_deleted = True

        super(BaseModelSoftDelete, self).save()

    def save(self, *args, **kwargs):
        if self.is_deleted and self.deleted_at is None:
            self.deleted_at = timezone.now()

        if not self.is_deleted and self.deleted_at is not None:
            self.deleted_at = None

        super(BaseModelSoftDelete, self).save(*args, **kwargs)
