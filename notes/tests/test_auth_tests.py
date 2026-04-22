from django.contrib.auth.models import User
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase


class AuthTests(APITestCase):
    def test_register_success(self):
        response = self.client.post(
            "/api/v1/auth/register/",
            {"username": "newuser", "password": "StrongPass123!"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], "user created")
        user = User.objects.get(username="newuser")
        self.assertFalse(user.is_staff)

    def test_register_duplicate_username_returns_error_shape(self):
        User.objects.create_user(username="existing", password="StrongPass123!")

        response = self.client.post(
            "/api/v1/auth/register/",
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
            "/api/v1/auth/login/",
            {"username": "alice", "password": "StrongPass123!"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_register_weak_password_returns_validation_error(self):
        response = self.client.post(
            "/api/v1/auth/register/",
            {"username": "weakuser", "password": "12345678"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["success"], False)
        self.assertIn("password", response.data["errors"])

    def test_register_staff_without_valid_key_is_rejected(self):
        response = self.client.post(
            "/api/v1/auth/register/",
            {
                "username": "staffcandidate",
                "password": "StrongPass123!",
                "role": "staff",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["success"], False)
        self.assertIn("role", response.data["errors"])
        self.assertFalse(User.objects.filter(username="staffcandidate").exists())

    @override_settings(STAFF_REGISTRATION_KEY="let-me-in")
    def test_register_staff_with_valid_key_creates_staff_user(self):
        response = self.client.post(
            "/api/v1/auth/register/",
            {
                "username": "staffuser",
                "password": "StrongPass123!",
                "role": "staff",
                "staff_registration_key": "let-me-in",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username="staffuser")
        self.assertTrue(user.is_staff)

    def test_me_requires_authentication(self):
        response = self.client.get("/api/v1/auth/me/")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["success"], False)

    def test_me_returns_role_user_for_normal_user(self):
        user = User.objects.create_user(username="profileuser", password="StrongPass123!")
        self.client.force_authenticate(user=user)

        response = self.client.get("/api/v1/auth/me/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "profileuser")
        self.assertEqual(response.data["role"], "user")
        self.assertEqual(response.data["is_staff"], False)

    def test_me_returns_role_staff_for_staff_user(self):
        user = User.objects.create_user(
            username="profilestaff", password="StrongPass123!", is_staff=True
        )
        self.client.force_authenticate(user=user)

        response = self.client.get("/api/v1/auth/me/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "profilestaff")
        self.assertEqual(response.data["role"], "staff")
        self.assertEqual(response.data["is_staff"], True)
