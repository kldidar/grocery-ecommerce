import uuid

from django.db import models
from django_stubs_ext.db.models import TypedModelMeta


class UUIDMixin(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    class Meta(TypedModelMeta):
        abstract = True


class TimestampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta(TypedModelMeta):
        abstract = True
        ordering = ["-created_at"]


class BaseModel(UUIDMixin, TimestampMixin):
    class Meta(TypedModelMeta):
        abstract = True
        ordering = ["-created_at"]
