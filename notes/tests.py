from django.contrib.auth.models import User
from django.urls import reverse #to get url from name in urls.py
from rest_framework import status # to get status codes like HTTP_200_OK, HTTP_400_BAD_REQUEST, etc.
from rest_framework.test import APITestCase # to create test cases for API endpoints, provides tools for making requests and checking responses

from .models import Note, Tag


class AuthTests(APITestCase):
    def test_register_success(self):
        response = self.client.post( # self.client is provided by APITestCase, allows us to make requests to our API endpoints
            "/api/auth/register/",
            {"username": "newuser", "password": "StrongPass123!"},
            format="json",
        )
                        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)# check response which indicates that the user was successfully created
        self.assertEqual(response.data["status"], "user created")
        self.assertTrue(User.objects.filter(username="newuser").exists()) # check if user actually exist in db

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


class NoteAndTagPermissionTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username="owner", password="StrongPass123!")
        self.other_user = User.objects.create_user(
            username="other", password="StrongPass123!"
        )
        self.staff_user = User.objects.create_user(
            username="staff", password="StrongPass123!", is_staff=True
        )

        self.owner_tag = Tag.objects.create(name="owner-tag", owner=self.owner)
        self.other_tag = Tag.objects.create(name="other-tag", owner=self.other_user)

        self.owner_note = Note.objects.create(
            title="Owner note", content="mine", owner=self.owner
        )
        self.other_note = Note.objects.create(
            title="Other note", content="not mine", owner=self.other_user
        )

    def test_unauthenticated_user_cannot_list_notes(self):
        response = self.client.get(reverse("note-list"))
    
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["success"], False)

    def test_owner_only_sees_own_notes(self):
        self.client.force_authenticate(user=self.owner)

        response = self.client.get(reverse("note-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.owner_note.id)

    def test_staff_can_see_all_notes(self):
        self.client.force_authenticate(user=self.staff_user)

        response = self.client.get(reverse("note-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_create_note_with_other_users_tag_fails(self):
        self.client.force_authenticate(user=self.owner)

        response = self.client.post(
            reverse("note-list"),
            {
                "title": "Invalid tags",
                "content": "Tag ownership check",
                "tag_ids": [self.other_tag.id],
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["success"], False)
        self.assertEqual(response.data["message"], "Bad request")

    def test_favorite_action_toggles_flag(self):
        self.client.force_authenticate(user=self.owner)

        response = self.client.patch(
            reverse("note-favorite", kwargs={"pk": self.owner_note.pk}), format="json"
        )
        self.owner_note.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.owner_note.is_favorite)

    def test_non_owner_cannot_delete_note(self):
        self.client.force_authenticate(user=self.other_user)

        response = self.client.delete(
            reverse("note-detail", kwargs={"pk": self.owner_note.pk})
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_staff_can_delete_any_note(self):
        self.client.force_authenticate(user=self.staff_user)

        response = self.client.delete(
            reverse("note-detail", kwargs={"pk": self.owner_note.pk})
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
