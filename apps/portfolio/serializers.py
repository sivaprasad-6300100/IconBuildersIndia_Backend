from rest_framework import serializers
from .models import PortfolioProject, ProjectImage


class ProjectImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    project_title = serializers.CharField(source='project.title', read_only=True)
    project_location = serializers.CharField(source='project.location', read_only=True)

    class Meta:
        model = ProjectImage
        fields = ['id', 'image_url', 'caption', 'order', 'project_title', 'project_location']

    def get_image_url(self, obj):
        return obj.image.url if obj.image else None


class PortfolioProjectListSerializer(serializers.ModelSerializer):
    """Matches the shape ProjectShowcase.jsx already expects for cards."""
    image = serializers.SerializerMethodField()
    desc = serializers.CharField(source='description')
    image_count = serializers.ReadOnlyField()

    class Meta:
        model = PortfolioProject
        fields = [
            'id', 'title', 'category', 'location', 'beds', 'area',
            'budget', 'status', 'progress', 'image', 'desc', 'image_count',
        ]

    def get_image(self, obj):
        if obj.cover_image:
            return obj.cover_image.url
        # No dedicated cover image set — fall back to the first gallery
        # photo so the card isn't blank just because the admin only
        # used "Upload Photos" and never separately picked a cover.
        first_image = obj.gallery_images.order_by('order', 'created_at').first()
        return first_image.image.url if first_image else None


class PortfolioProjectAdminSerializer(serializers.ModelSerializer):
    """
    Used by the React Admin Panel to create/edit a portfolio project.
    cover_image is a plain file upload (multipart/form-data).
    """
    cover_image = serializers.ImageField(required=False, allow_null=True)
    image_count = serializers.ReadOnlyField()

    class Meta:
        model = PortfolioProject
        fields = [
            'id', 'title', 'category', 'location', 'beds', 'area', 'budget',
            'status', 'progress', 'description', 'cover_image', 'is_published',
            'order', 'image_count', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class PortfolioProjectDetailSerializer(serializers.ModelSerializer):
    """
    Project meta for the gallery page header.
    NOTE: does NOT include the image list — with 200-300 images per
    project, those are fetched separately (paginated) so the page
    loads fast. See ProjectImageListView.
    """
    cover_image_url = serializers.SerializerMethodField()
    image_count = serializers.ReadOnlyField()

    class Meta:
        model = PortfolioProject
        fields = [
            'id', 'title', 'category', 'location', 'beds', 'area', 'budget',
            'status', 'progress', 'description', 'cover_image_url', 'image_count',
        ]

    def get_cover_image_url(self, obj):
        if obj.cover_image:
            return obj.cover_image.url
        # Same fallback as the list serializer — keeps the gallery header
        # image consistent with what the card shows.
        first_image = obj.gallery_images.order_by('order', 'created_at').first()
        return first_image.image.url if first_image else None