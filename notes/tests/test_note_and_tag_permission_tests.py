from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from notes.models import Note, Tag


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

    def test_owner_only_sees_own_tags(self):
        self.client.force_authenticate(user=self.owner)

        response = self.client.get(reverse("tag-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.owner_tag.id)

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

    def test_create_note_sets_owner_to_authenticated_user(self):
        self.client.force_authenticate(user=self.owner)

        response = self.client.post(
            reverse("note-list"),
            {
                "title": "Owner assignment",
                "content": "Owner should be request user",
                "owner": self.other_user.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created_note = Note.objects.get(id=response.data["id"])
        self.assertEqual(created_note.owner, self.owner)

    def test_update_note_replaces_tags_when_tag_ids_provided(self):
        self.client.force_authenticate(user=self.owner)
        extra_owner_tag = Tag.objects.create(name="owner-tag-2", owner=self.owner)
        self.owner_note.tags.add(self.owner_tag)

        response = self.client.patch(
            reverse("note-detail", kwargs={"pk": self.owner_note.pk}),
            {"tag_ids": [extra_owner_tag.id]},
            format="json",
        )
        self.owner_note.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            list(self.owner_note.tags.values_list("id", flat=True)),
            [extra_owner_tag.id],
        )

    def test_favorite_action_toggles_flag(self):
        self.client.force_authenticate(user=self.owner)

        response = self.client.patch(
            reverse("note-favorite", kwargs={"pk": self.owner_note.pk}), format="json"
        )
        self.owner_note.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.owner_note.is_favorite)

    def test_non_owner_cannot_toggle_favorite(self):
        self.client.force_authenticate(user=self.other_user)

        response = self.client.patch(
            reverse("note-favorite", kwargs={"pk": self.owner_note.pk}),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["success"], False)

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
