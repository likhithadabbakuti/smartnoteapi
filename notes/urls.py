from rest_framework.routers import DefaultRouter
from .views import NoteViewSet, TagViewSet

router=DefaultRouter()
#to create a router for the viewsets automatically creates the URL patterns
#  for the viewsets need of path() 

router.register('notes', NoteViewSet)
router.register('tags', TagViewSet)
# “Create API endpoints for Notes and Tags using these ViewSets”

urlpatterns = router.urls 
#attach all the generated URL patterns to the urls to django
