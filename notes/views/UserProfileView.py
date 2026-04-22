from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        role = "staff" if user.is_staff else "user"

        return Response(
            {
                "id": user.id,
                "username": user.username,
                "role": role,
                "is_staff": user.is_staff,
            }
        )
