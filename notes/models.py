from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Tag(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100,unique=True)
    owner = models.ForeignKey(User,on_delete=models.CASCADE)
    def __str__(self):
        return self.name
class Note(models.Model):
    
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)
    is_favorite = models.BooleanField(default=False)

    owner = models.ForeignKey(User,on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    