import uuid
from django.db import models
from django.conf import settings


class Notification(models.Model):
    ICON_CHOICES = [
        ('camera',   'Camera'),
        ('check',    'Check'),
        ('wallet',   'Wallet'),
        ('download', 'Download'),
        ('bell',     'Bell'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
    )

    text     = models.CharField(max_length=255)
    icon     = models.CharField(max_length=20, choices=ICON_CHOICES, default='bell')
    is_read  = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} — {self.text[:40]} ({'read' if self.is_read else 'unread'})"