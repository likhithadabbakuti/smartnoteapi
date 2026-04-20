from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase


class AuthTests(APITestCase):
    def test_register_success(self):
        response = self.client.post(
            "/api/auth/register/",
            {"username": "newuser", "password": "StrongPass123!"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], "user created")
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_register_duplicate_username_returns_error_shape(self):
        User.objects.create_user(username="existing", password="StrongPass123!")

        response = self.client.post(
            "/api/auth/register/",
            {"username": "existing", "password": "StrongPass123!"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["success"], False)
        self.assertEqual(response.data["message"], "Bad request")
        self.assertIn("username", response.data["errors"])

    def test_login_returns_access_and_refresh_tokens(self):
        User.objects.create_user(username="alice", password="StrongPass123!")

        response = self.client.post(
            "/api/auth/login/",
            {"username": "alice", "password": "StrongPass123!"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_register_weak_password_returns_validation_error(self):
        response = self.client.post(
            "/api/auth/register/",
            {"username": "weakuser", "password": "12345678"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["success"], False)
        self.assertIn("password", response.data["errors"])
