from datetime import timedelta

import graphene
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password, make_password
from django.http import HttpResponse
from django.utils import timezone
from graphene_django import DjangoObjectType
from graphql import GraphQLError

from .models import RefreshToken
from .utils import (
    create_access_token,
    create_email_token,
    create_refresh_token,
    decode_email_token,
    decode_token,
    send_activation_email,
    send_reset_password_email,
)

User = get_user_model()


# GraphQL Types
class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = ("id", "username", "email", "is_staff", "date_joined")


class RefreshTokenType(DjangoObjectType):
    class Meta:
        model = RefreshToken
        fields = ("id", "token", "revoked", "created_at", "expires_at")


class RefreshTokenQuery(graphene.ObjectType):
    my_tokens = graphene.List(RefreshTokenType)

    def resolve_my_tokens(self, info):
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError("Authentication required.")

        return RefreshToken.objects.filter(user=user).order_by("-created_at")


class UserQuery(graphene.ObjectType):
    me = graphene.Field(UserType)
    users = graphene.List(UserType)

    def resolve_me(self, info):
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError("Authentication required.")
        return user

    def resolve_users(self, info):
        user = info.context.user
        if not user.is_authenticated or not user.is_staff:
            raise GraphQLError("Admin privileges required.")
        return User.objects.all()


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

        username_base = email.split("@")[0]
        username = username_base
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{username_base}_{counter}"
            counter += 1
        # Create user
        user = User.objects.create(username=username, email=email, is_active=False)
        user.set_password(password1)
        user.save()

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
        try:
            payload = decode_email_token(token, "activate")
            user = User.objects.get(id=payload["user_id"])
            if user.is_active:
                raise GraphQLError("Account already activated")
            user.is_active = True
            user.save()
            return ActivateAccount(success=True)
        except User.DoesNotExist:
            raise GraphQLError("User not found")
        except Exception as e:
            raise GraphQLError(f"Activation failed: {str(e)}")


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
        response = HttpResponse()
        response.set_cookie(
            settings.JWT_COOKIE_NAME,
            refresh,
            max_age=int(settings.JWT_REFRESH_EXPIRATION.total_seconds()),
            httponly=True,
            samesite=settings.JWT_COOKIE_SAMESITE,
            secure=settings.JWT_COOKIE_SECURE,
            path="/",
        )
        # info.context.set_cookie(
        #     settings.JWT_COOKIE_NAME,
        #     refresh,
        #     max_age=int(settings.JWT_REFRESH_EXPIRATION.total_seconds()),
        #     httponly=True,
        #     samesite=settings.JWT_COOKIE_SAMESITE,
        #     secure=settings.JWT_COOKIE_SECURE,
        #     path="/",
        # )
        # info.context.COOKIES["refresh_token"] = refresh
        # info.context.COOKIES["refresh_token"]["httponly"] = True
        # info.context.COOKIES["refresh_token"]["samesite"] = "Strict"
        # info.context.COOKIES["refresh_token"]["path"] = "/"

        return Login(access_token=access, success=True)


class RefreshTokenMutation(graphene.Mutation):
    access_token = graphene.String()

    def mutate(self, info):
        cookie = info.context.COOKIES.get(settings.JWT_COOKIE_NAME)  # Fixed: COOKIES
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
        try:
            user = User.objects.filter(email=email).first()
            if not user:
                # Don't reveal if user exists or not for security
                return ForgotPassword(success=True)

            send_reset_password_email(user)
            return ForgotPassword(success=True)
        except Exception as e:
            raise GraphQLError(f"Failed to send reset email: {str(e)}")


class ResetPassword(graphene.Mutation):
    success = graphene.Boolean()

    class Arguments:
        token = graphene.String(required=True)
        password1 = graphene.String(required=True)
        password2 = graphene.String(required=True)

    def mutate(self, info, token, password1, password2):
        if password1 != password2:
            raise GraphQLError("Passwords do not match")
        try:
            payload = decode_email_token(token, "reset")
            user = User.objects.get(id=payload["user_id"])
            user.set_password(password1)
            user.save()
            return ResetPassword(success=True)
        except User.DoesNotExist:
            raise GraphQLError("User not found or invalid token")
        except Exception as e:
            raise GraphQLError(f"Password reset failed: {str(e)}")


class UpdateUser(graphene.Mutation):
    user = graphene.Field(UserType)

    class Arguments:
        username = graphene.String()
        email = graphene.String()
        password = graphene.String()

    def mutate(self, info, username=None, email=None, password=None):
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError("Authentication required.")

        if username:
            user.username = username
        if email:
            user.email = email
        if password:
            user.password = make_password(password)
        user.save()
        return UpdateUser(user=user)


class DeleteUser(graphene.Mutation):
    message = graphene.String()

    def mutate(self, info):
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError("Authentication required.")
        username = user.username
        user.delete()
        return DeleteUser(message=f"User '{username}' deleted successfully.")


class AdminDeleteUser(graphene.Mutation):
    message = graphene.String()

    class Arguments:
        user_id = graphene.ID(required=True)

    def mutate(self, info, user_id):
        user = info.context.user
        if not user.is_authenticated or not user.is_staff:
            raise GraphQLError("Admin privileges required.")

        try:
            target = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            raise GraphQLError("User not found.")
        target.delete()
        return AdminDeleteUser(message=f"User {target.username} deleted by admin.")


# --- Revoke Single Token ---
class RevokeToken(graphene.Mutation):
    message = graphene.String()

    class Arguments:
        token_id = graphene.ID(required=True)

    def mutate(self, info, token_id):
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError("Authentication required.")

        try:
            token = RefreshToken.objects.get(id=token_id, user=user)
        except RefreshToken.DoesNotExist:
            raise GraphQLError("Token not found or not owned by user.")

        token.revoke()
        return RevokeToken(message="Token revoked successfully.")


# --- Revoke All Tokens for Current User ---
class RevokeAllTokens(graphene.Mutation):
    message = graphene.String()

    def mutate(self, info):
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError("Authentication required.")

        tokens = RefreshToken.objects.filter(user=user, revoked=False)
        count = tokens.count()
        for token in tokens:
            token.revoke()

        return RevokeAllTokens(message=f"{count} active tokens revoked.")


# --- Admin: Revoke Any Token ---
class AdminRevokeToken(graphene.Mutation):
    message = graphene.String()

    class Arguments:
        token_id = graphene.ID(required=True)

    def mutate(self, info, token_id):
        user = info.context.user
        if not user.is_authenticated or not user.is_staff:
            raise GraphQLError("Admin privileges required.")

        try:
            token = RefreshToken.objects.get(id=token_id)
        except RefreshToken.DoesNotExist:
            raise GraphQLError("Token not found.")

        token.revoke()
        return AdminRevokeToken(message=f"Token {token.id} revoked by admin.")


class AccountQuery(UserQuery, RefreshTokenQuery, graphene.ObjectType):
    pass


class AccountMutation(graphene.ObjectType):
    register = Register.Field()
    activate_account = ActivateAccount.Field()
    login = Login.Field()
    refresh_token = RefreshTokenMutation.Field()
    logout = Logout.Field()
    forgot_password = ForgotPassword.Field()
    reset_password = ResetPassword.Field()
    update_user = UpdateUser.Field()
    delete_user = DeleteUser.Field()
    delete_admin_user = AdminDeleteUser.Field()
    revoke_token = RevokeToken.Field()
    revoke_all_tokens = RevokeAllTokens.Field()
    admin_revoke_token = AdminRevokeToken.Field()
