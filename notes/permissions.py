from rest_framework.permissions import BasePermission
#to create a custom permission class that checks if the user is the owner of the object

class IsOwner(BasePermission): #to check if the user is the owner of the object
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user
