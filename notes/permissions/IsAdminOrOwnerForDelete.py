from rest_framework.permissions import BasePermission


class IsAdminOrOwnerForDelete(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if getattr(view, "action", None) == "destroy":
            return obj.owner == request.user or request.user.is_staff
        return True
