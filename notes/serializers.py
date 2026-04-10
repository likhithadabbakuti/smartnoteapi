from rest_framework import serializers
from .models import Note,Tag
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']

class NoteSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)#to display the tags in the note serializer
    tag_ids = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True, write_only=True, required=False)
     #to accept tag ids when creating or updating a note   

    class Meta:
        model = Note
        fields = '__all__'
        read_only_fields = ['owner', 'created_at', 'updated_at']

    def validate(self, data): #checking the tags belong to the user or not
        user=self.context['request'].user #get the user from the request context
        tags=data.get('tag_ids',[])#get the tags from the validated data
        for tag in tags:
            if tag.owner != user:
                raise serializers.ValidationError(f"Tag '{tag.name}' does not belong to the user.")
        return data
    
    def create(self, validated_data): #handling the many-to-many relationship when creating a note
        tags = validated_data.pop('tag_ids', []) #remove tags
        note=Note.objects.create(**validated_data) #create the note
        note.tags.set(tags) #associate the tags with the note
        return note

    def update(self, instance, validated_data):
        tags = validated_data.pop('tag_ids', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if tags is not None:
            instance.tags.set(tags)
        return instance


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, min_length=8)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value

    def validate_password(self, value):
        try:
            validate_password(value)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(list(exc.messages))
        return value

    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data["username"],
            password=validated_data["password"],
        )
