from django.db import models


class PlatformSettings(models.Model):
    """Singleton — always pk=1, one row only."""
    id = models.PositiveSmallIntegerField(primary_key=True, default=1)

    platform_name = models.CharField(max_length=255, default='ReliaState')
    contact_email = models.EmailField(default='hello@iconbuilderindia.com')
    whatsapp_number = models.CharField(max_length=20, default='+91 98765 43210')
    domain = models.CharField(max_length=255, default='iconbuilderindia.com')

    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass  # prevent deletion of the singleton row

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return self.platform_name