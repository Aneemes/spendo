import uuid
from django.db import models
from django.utils import timezone
from django.conf import settings

class IdentifierTimeStampAbstractModel(models.Model):
    """
    An abstract base class model that provides self-updating 'created_at' and 'updated_at' fields,
    along with a unique 'uid' field.
    Attributes:
        uid (UUIDField): A unique identifier for the model instance, generated automatically.
        created_at (DateTimeField): The date and time when the model instance was created.
        updated_at (DateTimeField): The date and time when the model instance was last updated.
    Meta:
        abstract (bool): Indicates that this is an abstract base class and should not be used to create any database table.
    """
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name="Public Identifier")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        