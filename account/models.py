from datetime import timedelta
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from .managers import CustomUserManager
from core.models_mixin import IdentifierTimeStampAbstractModel 


class CustomUser(AbstractUser, IdentifierTimeStampAbstractModel):
    """
    CustomUser model that extends AbstractUser and IdentifierTimeStampAbstractModel.
    Attributes:
        username (CharField): A unique username with a maximum length of 11 characters.
        email (EmailField): A unique email address used as the USERNAME_FIELD.
        full_name (CharField): The full name of the user with a maximum length of 125 characters.
        USERNAME_FIELD (str): The field used for authentication, set to 'email'.
        REQUIRED_FIELDS (list): A list of fields that are required when creating a user via createsuperuser.
        objects (CustomUserManager): The manager for the CustomUser model.
    Methods:
        __str__(): Returns the email of the user as the string representation.
    """
    username = models.CharField(max_length=11, unique=True)
    email = models.EmailField(_("email address"), unique=True)
    full_name = models.CharField(max_length=125)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email
    
class EmailConfirmationToken(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="email_confirmation_token")
    created_time = models.DateTimeField(auto_now=True)
    token = models.CharField(max_length=64)
    email = models.EmailField(max_length=255, null=True)

    class Meta:
        verbose_name = "Email Confirmation Token"
        verbose_name_plural = "Email Confirmation Tokens"
        ordering = ["-created_time"]

    def __str__(self):
        return self.user.username + self.email
    
    @property
    def has_expired(self) -> bool:
        now = timezone.now()
        expiry_time = self.created_time + timedelta(minutes=5)
        return now > expiry_time