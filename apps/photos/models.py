import uuid
from django.db import models
from django.conf import settings
from cloudinary.models import CloudinaryField

from apps.projects.models import Project, Milestone


class ProjectPhoto(models.Model):
    CATEGORY_CHOICES = (
        ('before', 'Before'),
        ('progress', 'Progress'),
        ('after', 'After'),
        ('issue', 'Issue / Defect'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='photos')
    milestone = models.ForeignKey(
        Milestone, on_delete=models.SET_NULL, related_name='photos',
        null=True, blank=True,
    )

    image = CloudinaryField('image')
    caption = models.CharField(max_length=255, blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='progress')

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='uploaded_photos',
        null=True,
    )

    is_active = models.BooleanField(default=True)  # soft delete
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.project.name} - {self.category} ({self.created_at.date()})"
