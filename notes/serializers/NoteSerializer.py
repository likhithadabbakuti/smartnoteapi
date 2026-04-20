from rest_framework import serializers

from notes.models import Note, Tag
from .TagSerializer import TagSerializer


class NoteSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True, write_only=True, required=False
    )

    class Meta:
        model = Note
        fields = "__all__"
        read_only_fields = ["owner", "created_at", "updated_at"]

    def validate(self, data):
        user = self.context["request"].user
        tags = data.get("tag_ids", [])
        for tag in tags:
            if tag.owner != user:
                raise serializers.ValidationError(
                    f"Tag '{tag.name}' does not belong to the user."
                )
        return data

    def create(self, validated_data):
        tags = validated_data.pop("tag_ids", [])
        note = Note.objects.create(**validated_data)
        note.tags.set(tags)
        return note

    def update(self, instance, validated_data):
        tags = validated_data.pop("tag_ids", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if tags is not None:
            instance.tags.set(tags)
        return instance
