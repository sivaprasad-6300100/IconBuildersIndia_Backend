from django.contrib import admin
from .models import OTPStore


@admin.register(OTPStore)
class OTPStoreAdmin(admin.ModelAdmin):
    list_display  = ['phone', 'otp', 'is_used', 'created_at', 'expires_at']
    list_filter   = ['is_used']
    search_fields = ['phone']
    ordering      = ['-created_at']
    readonly_fields = ['created_at', 'expires_at']