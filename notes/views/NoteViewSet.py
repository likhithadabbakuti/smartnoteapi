from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from notes.models import Note
from notes.permissions import (
    IsAdminOrOwnerForDelete,
    IsAuthenticatedUser,
    IsOwnerOrStaff,
)
from notes.serializers import NoteSerializer


class NoteViewSet(ModelViewSet):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticatedUser, IsOwnerOrStaff]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["is_favorite", "tags"]
    search_fields = ["title", "content"]
    ordering_fields = ["created_at"]

    def get_permissions(self):
        if self.action == "destroy":
            return [IsAuthenticatedUser(), IsAdminOrOwnerForDelete()]
        return [permission() for permission in self.permission_classes]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Note.objects.all()
        if self.request.user.is_authenticated:
            return Note.objects.filter(owner=self.request.user)
        return Note.objects.none()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=["patch"])
    def favorite(self, request, pk=None):
        note = self.get_object()
        note.is_favorite = not note.is_favorite
        note.save()
        return Response({"status": "favorite status updated"})
