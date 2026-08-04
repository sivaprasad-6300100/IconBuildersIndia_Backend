import uuid
from django.db import models
from django.conf import settings


class Inquiry(models.Model):

    STATUS_CHOICES = [
        ('new',       'New'),
        ('called',    'Called'),
        ('converted', 'Converted'),
        ('closed',    'Closed'),
    ]

    TYPE_CHOICES = [
        ('new_construction', 'New Construction'),
        ('renovation',       'Renovation'),
        ('commercial',       'Commercial'),
        ('interior',         'Interior Design'),
        ('other',            'Other'),
    ]

    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Lead details
    name         = models.CharField(max_length=100)
    phone        = models.CharField(max_length=15)
    email        = models.EmailField(blank=True, null=True)
    city         = models.CharField(max_length=100, blank=True)
    inquiry_type = models.CharField(max_length=30, choices=TYPE_CHOICES, default='new_construction')
    plot_size    = models.CharField(max_length=50, blank=True)
    message      = models.TextField(blank=True)

    # Admin tracking
    status       = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    admin_note   = models.TextField(blank=True)       # admin internal note
    assigned_to  = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='assigned_inquiries'
    )

    # Source tracking
    source       = models.CharField(max_length=50, default='website')  # website / estimator / whatsapp

    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'inquiries'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} — {self.phone} ({self.status})"