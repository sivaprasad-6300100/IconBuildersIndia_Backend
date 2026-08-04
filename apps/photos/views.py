from rest_framework import generics, permissions
from apps.auth_app.permissions import IsAdmin, IsContractor
from .models import ProjectPhoto
from .serializers import ProjectPhotoSerializer


class ProjectPhotoListCreateView(generics.ListCreateAPIView):
    """
    List/upload photos for a project.
    - Client & contractor: only see photos for their own project.
    - Admin & contractor: can upload. Client is read-only.
    """
    serializer_class = ProjectPhotoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = ProjectPhoto.objects.filter(
            project_id=self.kwargs['project_id'], is_active=True
        )
        if user.role == 'client':
            qs = qs.filter(project__client=user)
        elif user.role == 'contractor':
            qs = qs.filter(project__contractor=user)
        return qs

    def perform_create(self, serializer):
        serializer.save(
            project_id=self.kwargs['project_id'],
            uploaded_by=self.request.user,
        )

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated(), (IsAdmin | IsContractor)()]
        return [permissions.IsAuthenticated()]


class ProjectPhotoDetailView(generics.RetrieveDestroyAPIView):
    """Retrieve or soft-delete a single photo. Delete restricted to admin."""
    queryset = ProjectPhoto.objects.all()
    serializer_class = ProjectPhotoSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_permissions(self):
        if self.request.method == 'DELETE':
            return [IsAdmin()]
        return [permissions.IsAuthenticated()]

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()
