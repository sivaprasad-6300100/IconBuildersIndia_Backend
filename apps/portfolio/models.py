import uuid
from django.db import models
from cloudinary.models import CloudinaryField


class PortfolioProject(models.Model):
    """
    Public marketing showcase entry — this is what feeds your
    ProjectShowcase.jsx cards. Separate from the internal client
    Project model in apps/projects (that one tracks real client jobs;
    this one is public portfolio content).
    """
    CATEGORY_CHOICES = (
        ('Villa', 'Villa'),
        ('Apartment', 'Apartment'),
        ('Row House', 'Row House'),
        ('Plot', 'Plot'),
        ('Commercial', 'Commercial'),
    )
    STATUS_CHOICES = (
        ('Planning', 'Planning'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    title = models.CharField(max_length=255)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    location = models.CharField(max_length=100, default='Bangalore')
    beds = models.PositiveIntegerField(null=True, blank=True)
    area = models.CharField(max_length=50)          # e.g. "3200 sqft"
    budget = models.CharField(max_length=50)         # e.g. "₹1.8 Cr"
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Planning')
    progress = models.PositiveIntegerField(default=0)  # 0-100

    description = models.TextField(blank=True)
    cover_image = CloudinaryField('image', blank=True, null=True)  # shown on the card

    is_published = models.BooleanField(default=True)  # toggle visibility on public site
    order = models.PositiveIntegerField(default=0)     # manual sort order for the grid

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title

    @property
    def image_count(self):
        return self.gallery_images.count()


class ProjectImage(models.Model):
    """
    One row per gallery photo. A single PortfolioProject can have
    200-300+ of these — this is what the separate gallery page renders.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    project = models.ForeignKey(
        PortfolioProject, on_delete=models.CASCADE, related_name='gallery_images'
    )
    image = CloudinaryField('image')
    caption = models.CharField(max_length=255, blank=True)
    order = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"{self.project.title} - image {self.id}"