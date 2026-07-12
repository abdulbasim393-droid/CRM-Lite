from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User


class AuthTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = "/api/auth/register/"
        self.login_url = "/api/auth/login/"
        self.refresh_url = "/api/auth/refresh/"
        self.logout_url = "/api/auth/logout/"
        self.me_url = "/api/auth/me/"
        self.leads_url = "/api/leads/leads/"

        self.user_data = {
            "email": "test@example.com",
            "password": "testpass123",
            "confirm_password": "testpass123",
            "first_name": "Test",
            "last_name": "User",
            "role": "SALES_EXECUTIVE",
        }

    def _get_admin(self):
        return User.objects.create_superuser(
            email="admin@example.com",
            password="adminpass123",
        )

    def _login(self, email=None, password=None):
        return self.client.post(
            self.login_url,
            {
                "email": email or self.user_data["email"],
                "password": password or self.user_data["password"],
            },
            format="json",
        )

    def test_register_success(self):
        response = self.client.post(self.register_url, self.user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("user", response.data)
        self.assertEqual(response.data["user"]["email"], self.user_data["email"])

    def test_register_password_mismatch(self):
        data = {**self.user_data, "confirm_password": "different"}
        response = self.client.post(self.register_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_duplicate_email(self):
        self.client.post(self.register_url, self.user_data, format="json")
        response = self.client.post(self.register_url, self.user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_success(self):
        self.client.post(self.register_url, self.user_data, format="json")
        response = self._login()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertIn("user", response.data)

    def test_login_invalid_credentials(self):
        response = self._login(email="nonexist@test.com", password="wrong")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_disabled_user(self):
        self.client.post(self.register_url, self.user_data, format="json")
        User.objects.filter(email=self.user_data["email"]).update(is_active=False)
        response = self._login()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_protected_endpoint_without_token(self):
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_protected_endpoint_with_token(self):
        self.client.post(self.register_url, self.user_data, format="json")
        login_resp = self._login()
        token = login_resp.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.user_data["email"])

    def test_token_refresh(self):
        self.client.post(self.register_url, self.user_data, format="json")
        login_resp = self._login()
        refresh = login_resp.data["refresh"]
        response = self.client.post(
            self.refresh_url,
            {"refresh": refresh},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_refresh_with_invalid_token(self):
        response = self.client.post(
            self.refresh_url,
            {"refresh": "invalidtoken"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_success(self):
        self.client.post(self.register_url, self.user_data, format="json")
        login_resp = self._login()
        token = login_resp.data["access"]
        refresh = login_resp.data["refresh"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        response = self.client.post(
            self.logout_url,
            {"refresh": refresh},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_logout_without_auth(self):
        response = self.client.post(
            self.logout_url,
            {"refresh": "some_token"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
