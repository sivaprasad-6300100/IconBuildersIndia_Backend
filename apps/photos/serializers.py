from rest_framework import serializers
from .models import ProjectPhoto


class ProjectPhotoSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    uploaded_by_name = serializers.CharField(source='uploaded_by.name', read_only=True, default=None)

    class Meta:
        model = ProjectPhoto
        fields = [
            'id', 'project', 'milestone', 'image', 'image_url', 'caption',
            'category', 'uploaded_by', 'uploaded_by_name', 'is_active', 'created_at',
        ]
        read_only_fields = ['id', 'project', 'uploaded_by', 'created_at','is_active']

    def get_image_url(self, obj):
        return obj.image.url if obj.image else None