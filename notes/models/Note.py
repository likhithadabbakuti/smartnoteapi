from django.contrib.auth.models import User
from django.db import models

from .Tag import Tag


class Note(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)
    is_favorite = models.BooleanField(default=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
