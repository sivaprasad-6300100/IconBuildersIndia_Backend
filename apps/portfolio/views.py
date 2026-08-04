from rest_framework import generics, permissions, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from apps.auth_app.permissions import IsAdmin
from .models import PortfolioProject, ProjectImage
from .serializers import (
    PortfolioProjectListSerializer,
    PortfolioProjectDetailSerializer,
    PortfolioProjectAdminSerializer,
    ProjectImageSerializer,
)


class ImagePagination(PageNumberPagination):
    page_size = 30
    page_size_query_param = 'page_size'
    max_page_size = 100


class PortfolioProjectListView(generics.ListAPIView):
    """
    Public — feeds the ProjectShowcase.jsx card grid, and also the
    per-category page (?category=Villa) that lists all projects in
    that category before drilling into one project's own gallery.
    """
    serializer_class = PortfolioProjectListSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        qs = PortfolioProject.objects.filter(is_published=True)
        category = self.request.query_params.get('category')
        if category:
            qs = qs.filter(category__iexact=category)
        return qs


class PortfolioProjectDetailView(generics.RetrieveAPIView):
    """Public — project meta for the gallery page header."""
    serializer_class = PortfolioProjectDetailSerializer
    permission_classes = [permissions.AllowAny]
    queryset = PortfolioProject.objects.filter(is_published=True)
    lookup_field = 'id'


class ProjectImageListView(generics.ListAPIView):
    """
    Public — paginated gallery images for one project (30 per page).
    Frontend calls this repeatedly (infinite scroll / "load more")
    instead of pulling all 200-300 images in one request.
    """
    serializer_class = ProjectImageSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = ImagePagination

    def get_queryset(self):
        return ProjectImage.objects.filter(project_id=self.kwargs['project_id'])


# ── Admin-only endpoints (used by the React Admin Panel, not Django admin) ──

class PortfolioProjectAdminListCreateView(generics.ListCreateAPIView):
    """
    Admin panel: list ALL projects (published + unpublished) and create
    a new one with title/category/location/etc + optional cover image.
    """
    serializer_class = PortfolioProjectAdminSerializer
    permission_classes = [IsAdmin]
    # JSONParser included alongside the file-upload parsers so this view
    # can also handle plain-JSON requests (not just multipart creates).
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    queryset = PortfolioProject.objects.all()


class PortfolioProjectAdminDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Admin panel: edit or delete a single project (e.g. toggle is_published).

    Needs both multipart parsers (for cover_image file uploads) AND
    JSONParser (for simple JSON PATCH requests like the Publish/Unpublish
    toggle, which sends {"is_published": true} with no file attached).
    Without JSONParser, a JSON PATCH gets rejected with 415 Unsupported
    Media Type because the view didn't know how to read that format.
    """
    serializer_class = PortfolioProjectAdminSerializer
    permission_classes = [IsAdmin]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    queryset = PortfolioProject.objects.all()
    lookup_field = 'id'


class PortfolioBulkImageUploadView(APIView):
    """
    Admin panel: upload many gallery images (200-300+) to one project
    in a single request. Frontend sends multipart/form-data with all
    files under the same field name 'images'.
    """
    permission_classes = [IsAdmin]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, project_id):
        try:
            project = PortfolioProject.objects.get(id=project_id)
        except PortfolioProject.DoesNotExist:
            return Response({'detail': 'Project not found.'}, status=status.HTTP_404_NOT_FOUND)

        files = request.FILES.getlist('images')
        if not files:
            return Response({'detail': 'No images provided.'}, status=status.HTTP_400_BAD_REQUEST)

        start_order = project.gallery_images.count()
        created = []
        for i, f in enumerate(files):
            img = ProjectImage.objects.create(project=project, image=f, order=start_order + i)
            created.append(img.id)

        return Response(
            {'uploaded': len(created), 'total_images': project.gallery_images.count()},
            status=status.HTTP_201_CREATED,
        )