from rest_framework import serializers
from .models import PlatformSettings


class PlatformSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlatformSettings
        fields = ['platform_name', 'contact_email', 'whatsapp_number', 'domain', 'updated_at']
        read_only_fields = ['updated_at']