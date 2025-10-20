import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta


def default_expiry():
    return timezone.now() + timedelta(days=7)


class User(AbstractUser):
    pass


class RefreshToken(models.Model):
    """
    A refresh token model with blacklist capability.

    Each token is associated with a specific user and can be revoked
    (blacklisted) if needed. Tokens also have an expiration date.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="refresh_tokens",
        help_text="The user associated with this refresh token.",
    )
    token = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        help_text="A unique UUID identifier for the token.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the token was created.",
    )
    revoked = models.BooleanField(
        default=False,
        help_text="Indicates whether the token has been revoked (blacklisted).",
    )
    expires_at = models.DateTimeField(
        default=default_expiry,
        help_text="Expiration date and time for the token (default 7 days from creation).",
    )

    def is_valid(self):
        """
        Check if the token is still valid.

        A token is considered valid if:
        1. It has not been revoked.
        2. It has not expired.

        Returns:
            bool: True if the token is valid, False otherwise.

        Example:
            >>> token = RefreshToken.objects.first()
            >>> token.is_valid()
            True
        """
        return not self.revoked and timezone.now() < self.expires_at

    def revoke(self):
        """
        Revoke (blacklist) the token.

        Sets `revoked` to True and saves the model instance.
        This prevents further use of the token.

        Example:
            >>> token = RefreshToken.objects.first()
            >>> token.revoke()
            >>> token.revoked
            True
        """
        self.revoked = True
        self.save()

    def __str__(self):
        """
        String representation of the token.

        Returns:
            str: A string showing the user's email and the token UUID.
        """
        return f"{self.user.email} - {self.token}"
