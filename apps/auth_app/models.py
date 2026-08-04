from django.db import models
from django.utils import timezone
from datetime import timedelta


class OTPStore(models.Model):
    phone      = models.CharField(max_length=15)
    otp        = models.CharField(max_length=6)
    is_used    = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = 'auth_app'
        db_table  = 'otp_store'
        ordering  = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=10)
        super().save(*args, **kwargs)

    def is_valid(self):
        return (
            not self.is_used and
            timezone.now() < self.expires_at
        )

    def __str__(self):
        return f"OTP for {self.phone} — {'Used' if self.is_used else 'Active'}"