import uuid
from django.db import models
from django.conf import settings
from apps.projects.models import Project, Milestone


class Payment(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid',    'Paid'),
    ]

    METHOD_CHOICES = [
        ('cash',         'Cash'),
        ('bank_transfer','Bank Transfer'),
        ('upi',          'UPI'),
        ('cheque',       'Cheque'),
    ]

    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project     = models.ForeignKey(Project,   on_delete=models.CASCADE,  related_name='payments')
    milestone   = models.ForeignKey(Milestone, on_delete=models.SET_NULL, related_name='payments', null=True, blank=True)

    # Payment details
    milestone_name = models.CharField(max_length=200)         # e.g. "Foundation Complete"
    amount         = models.DecimalField(max_digits=12, decimal_places=2)
    method         = models.CharField(max_length=20, choices=METHOD_CHOICES, default='cash')
    status         = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Admin fills these manually after receiving payment
    paid_date      = models.DateField(null=True, blank=True)
    receipt_note   = models.CharField(max_length=500, blank=True)  # admin note

    # Who marked it paid
    marked_by      = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='payments_marked'
    )

    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payments'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.project.name} — {self.milestone_name} — ₹{self.amount} ({self.status})"