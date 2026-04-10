from .models import Note, Tag
from .serializers import NoteSerializer, TagSerializer, RegisterSerializer
from .permissions import IsOwner
from rest_framework.decorators import action #to create a custom action for marking a note as favorite
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend #to enable filtering in the viewset
from rest_framework.filters import SearchFilter,OrderingFilter
from rest_framework.views import APIView
from rest_framework import status
# Create your views here.
class NoteViewSet(ModelViewSet):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    permission_classes = [IsOwner]
    filter_backends = [DjangoFilterBackend,SearchFilter,OrderingFilter]#to enable filtering, searching and ordering in the viewset
    filterset_fields = ['is_favorite', 'tags'] #to filter notes by is_favorite and tags
    search_fields = ['title', 'content'] #to search notes by title and content
    ordering_fields = ['created_at'] #to order notes by created_at

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Note.objects.filter(owner=self.request.user)
        return Note.objects.none()#to return an empty queryset for unauthenticated users
    #to return only the notes that belong to the authenticated user

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
    #to set the owner of the note to the authenticated user when creating a note

    @action(detail=True, methods=['patch'])
    #to create a custom action for marking a note as favorite
    def favorite(self, request, pk=None):
        note = self.get_object() #get the note object
        note.is_favorite = not note.is_favorite #toggle the is_favorite field
        note.save() #save the note
        return Response({'status': 'favorite status updated'}) 
    

class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsOwner]

    def get_queryset(self):
        return Tag.objects.filter(owner=self.request.user) 
    #to return only the tags that belong to the authenticated user

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
    #to set the owner of the tag to the authenticated user when creating a tag

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'status': 'user created'}, status=status.HTTP_201_CREATED)
        
