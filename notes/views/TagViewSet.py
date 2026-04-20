from rest_framework.viewsets import ModelViewSet

from notes.models import Tag
from notes.permissions import (
    IsAdminOrOwnerForDelete,
    IsAuthenticatedUser,
    IsOwnerOrStaff,
)
from notes.serializers import TagSerializer


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticatedUser, IsOwnerOrStaff]

    def get_permissions(self):
        if self.action == "destroy":
            return [IsAuthenticatedUser(), IsAdminOrOwnerForDelete()]
        return [permission() for permission in self.permission_classes]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Tag.objects.all()
        return Tag.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
