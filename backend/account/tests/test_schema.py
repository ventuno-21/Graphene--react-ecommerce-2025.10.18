from django.test import TestCase
from django.contrib.auth import get_user_model
from graphene.test import Client
from account.schema import AccountMutation, AccountQuery
from account.models import RefreshToken
from unittest.mock import patch

User = get_user_model()


class BaseGraphQLTestCase(TestCase):
    def setUp(self):
        self.client = Client(schema=AccountMutation._meta.schema)
        self.user = User.objects.create_user(
            email="test@example.com", password="12345678", is_active=True
        )


class RegisterMutationTest(BaseGraphQLTestCase):
    def test_register_user(self):
        query = """
        mutation {
          register(email: "user@example.com", password1: "1234", password2: "1234") {
            success
            message
            email
          }
        }
        """
        response = self.client.execute(query)
        data = response["data"]["register"]

        self.assertTrue(data["success"])
        self.assertIn("Account created", data["message"])
        self.assertEqual(data["email"], "user@example.com")


class LoginMutationTest(BaseGraphQLTestCase):
    @patch("accounts.schema.create_access_token", return_value="fake_access")
    @patch("accounts.schema.create_refresh_token", return_value=("fake_refresh", None))
    def test_login_user(self, mock_refresh, mock_access):
        query = """
        mutation {
          login(email: "test@example.com", password: "12345678") {
            success
            accessToken
          }
        }
        """
        response = self.client.execute(query)
        data = response["data"]["login"]

        self.assertTrue(data["success"])
        self.assertEqual(data["accessToken"], "fake_access")
