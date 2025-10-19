# accounts/schema.py
from datetime import timedelta

import graphene
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password, make_password
from django.utils import timezone
from graphql import GraphQLError

from .models import RefreshToken
from .utils import (
    create_access_token,
    create_refresh_token,
    decode_token,
    create_email_token,
    decode_email_token,
    send_activation_email,
    send_reset_password_email,
)

User = get_user_model()


class Register(graphene.Mutation):
    user_id = graphene.Int()
    email = graphene.String()
    message = graphene.String()
    success = graphene.Boolean()

    class Arguments:
        email = graphene.String(required=True)
        password1 = graphene.String(required=True)
        password2 = graphene.String(required=True)

    def mutate(self, info, email, password1, password2):
        if User.objects.filter(email=email).exists():
            raise GraphQLError("Email already registered")
        if password1 != password2:
            raise GraphQLError("Passwords do not match")

        user = User.objects.create(
            email=email, password=make_password(password1), is_active=False
        )

        send_activation_email(user)
        return Register(
            user_id=user.id,
            email=user.email,
            message="Account created. Please check your email to activate your account.",
            success=True,
        )


class ActivateAccount(graphene.Mutation):
    success = graphene.Boolean()

    class Arguments:
        token = graphene.String(required=True)

    def mutate(self, info, token):
        payload = decode_email_token(token, "activate")
        user = User.objects.get(id=payload["user_id"])
        user.is_active = True
        user.save()
        return ActivateAccount(success=True)


class Login(graphene.Mutation):
    access_token = graphene.String()
    success = graphene.Boolean()

    class Arguments:
        email = graphene.String(required=True)
        password = graphene.String(required=True)

    def mutate(self, info, email, password):
        user = User.objects.filter(email=email).first()
        if not user:
            raise GraphQLError("Invalid credentials")
        if not check_password(password, user.password):
            raise GraphQLError("Invalid credentials")

        access = create_access_token(user)
        refresh, token_obj = create_refresh_token(user)

        # Set HttpOnly cookie
        info.context.cookies["refresh_token"] = refresh
        info.context.cookies["refresh_token"]["httponly"] = True
        info.context.cookies["refresh_token"]["samesite"] = "Strict"
        info.context.cookies["refresh_token"]["path"] = "/"

        return Login(access_token=access, success=True)


class RefreshTokenMutation(graphene.Mutation):
    access_token = graphene.String()

    def mutate(self, info):
        cookie = info.context.COOKIES.get("refresh_token")
        if not cookie:
            raise GraphQLError("Refresh token missing")

        payload = decode_token(cookie)
        if payload.get("type") != "refresh":
            raise GraphQLError("Invalid token type")

        try:
            token_obj = RefreshToken.objects.get(token=payload["token_id"])
        except RefreshToken.DoesNotExist:
            raise GraphQLError("Token revoked or invalid")

        if not token_obj.is_valid():
            raise GraphQLError("Token revoked or expired")

        access = create_access_token(token_obj.user)
        return RefreshTokenMutation(access_token=access)


class Logout(graphene.Mutation):
    success = graphene.Boolean()

    def mutate(self, info):
        cookie = info.context.COOKIES.get("refresh_token")
        if cookie:
            payload = decode_token(cookie)
            try:
                token_obj = RefreshToken.objects.get(token=payload["token_id"])
                token_obj.revoke()
            except RefreshToken.DoesNotExist:
                pass

        # Remove cookie
        info.context.cookies["refresh_token"] = ""
        info.context.cookies["refresh_token"]["max-age"] = 0

        return Logout(success=True)


class ForgotPassword(graphene.Mutation):
    success = graphene.Boolean()

    class Arguments:
        email = graphene.String(required=True)

    def mutate(self, info, email):
        user = User.objects.filter(email=email).first()
        if not user:
            raise GraphQLError("User not found")
        send_reset_password_email(user)
        return ForgotPassword(success=True)


class ResetPassword(graphene.Mutation):
    success = graphene.Boolean()

    class Arguments:
        token = graphene.String(required=True)
        password1 = graphene.String(required=True)
        password2 = graphene.String(required=True)

    def mutate(self, info, token, password1, password2):
        if password1 != password2:
            raise GraphQLError("Passwords do not match")
        payload = decode_email_token(token, "reset")
        user = User.objects.get(id=payload["user_id"])
        user.password = make_password(password1)
        user.save()
        return ResetPassword(success=True)


class Mutation(graphene.ObjectType):
    register = Register.Field()
    activate_account = ActivateAccount.Field()
    login = Login.Field()
    refresh_token = RefreshTokenMutation.Field()
    logout = Logout.Field()
    forgot_password = ForgotPassword.Field()
    reset_password = ResetPassword.Field()
