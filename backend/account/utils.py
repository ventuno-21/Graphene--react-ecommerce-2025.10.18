import os
from datetime import datetime, timezone, timedelta

import jwt
from django.conf import settings
from django.core.mail import send_mail
from dotenv import load_dotenv
from graphql import GraphQLError
from .models import RefreshToken

load_dotenv()  # take environment variables


FRONTEND_URL = os.getenv("{FRONTEND_URL}")


def create_access_token(user):
    exp = datetime.now(timezone.utc) + settings.JWT_ACCESS_EXPIRATION
    payload = {
        "user_id": user.id,
        "email": user.email,
        "type": "access",
        "exp": int(exp.timestamp()),
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    if isinstance(token, bytes):
        """
        PyJWT>=2 returns str; if bytes, decode
        Ensures that the given token is always returned as a string.

        If the `token` variable is of type `bytes`, it will be decoded to a UTF-8
        string using `token.decode()`. This guarantees consistent string handling
        regardless of whether the input originally comes as bytes or str.

        Args:
            token (bytes | str): The token value to normalize. It may be provided
                as raw bytes (e.g., b"abc123") or already as a string (e.g., "abc123").

        Returns:
            str: The decoded or unchanged string representation of the token.

        Examples:
            >>> normalize_token(b"abc123")
            'abc123'
            >>> normalize_token("xyz456")
            'xyz456'
            >>> normalize_token(b"üser_token")
            'üser_token'  # decoded using UTF-8
        """
        token = token.decode()
    return token


def create_refresh_token(user):
    token_obj = RefreshToken.objects.create(
        user=user, expires_at=timezone.now() + timedelta(days=7)
    )
    payload = {
        "token_id": str(token_obj.token),
        "email": user.email,
        "type": "refresh",
        "exp": token_obj.expires_at,
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    if isinstance(token, bytes):
        token = token.decode()
    return token, token_obj


def decode_token(token):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise GraphQLError("Token expired")
    except jwt.InvalidTokenError:
        raise GraphQLError("Invalid token")


def create_email_token(user, purpose="activate"):
    payload = {
        "user_id": user.id,
        "type": purpose,  # "activate" / "reset"
        "exp": datetime.now(timezone.utc) + timedelta(hours=24),
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    return token


def decode_email_token(token, purpose):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        if payload.get("type") != purpose:
            raise GraphQLError("Invalid token purpose")
        return payload
    except jwt.ExpiredSignatureError:
        raise GraphQLError("Token expired")
    except jwt.InvalidTokenError:
        raise GraphQLError("Invalid token")


def send_activation_email(user):
    token = create_email_token(user, "activate")
    activation_link = f"{FRONTEND_URL}/activate/?token={token}"
    send_mail(
        subject="Activate your account",
        message=f"Hi {user.email}, click to activate: {activation_link}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
    )


def send_reset_password_email(user):
    token = create_email_token(user, "reset")
    reset_link = f"{FRONTEND_URL}/reset-password/?token={token}"
    send_mail(
        subject="Reset your password",
        message=f"Hi {user.email}, click to reset password: {reset_link}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
    )
