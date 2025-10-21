import os
from datetime import timedelta
from django.utils import timezone  # Use Django's timezone
import jwt
from django.conf import settings
from django.core.mail import send_mail
from dotenv import load_dotenv
from graphql import GraphQLError
from .models import RefreshToken

load_dotenv()

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")


def create_access_token(user):
    exp = timezone.now() + settings.JWT_ACCESS_EXPIRATION  # Use timezone.now()
    payload = {
        "user_id": user.id,
        "email": user.email,
        "type": "access",
        "exp": int(exp.timestamp()),
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    if isinstance(token, bytes):
        token = token.decode()
    return token


def create_refresh_token(user):
    token_obj = RefreshToken.objects.create(
        user=user, expires_at=timezone.now() + timedelta(days=7)  # Use timezone.now()
    )
    payload = {
        "token_id": str(token_obj.token),
        "email": user.email,
        "type": "refresh",
        "exp": int(token_obj.expires_at.timestamp()),  # Convert to timestamp
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
        "type": purpose,
        "exp": timezone.now() + timedelta(hours=24),  # Use timezone.now()
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    if isinstance(token, bytes):
        token = token.decode()
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
    reset_link = f"{FRONTEND_URL}/reset-password/?{token}"
    send_mail(
        subject="Reset your password",
        message=f"Hi {user.email}, click to reset password: {reset_link}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
    )
