from django.contrib import admin
from .models import Inquiry


@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display   = ['name', 'phone', 'city', 'inquiry_type', 'plot_size', 'status', 'source', 'created_at']
    list_filter    = ['status', 'inquiry_type', 'source']
    search_fields  = ['name', 'phone', 'email', 'city']
    ordering       = ['-created_at']
    readonly_fields = ['id', 'created_at', 'updated_at']

    fieldsets = (
        ('Lead Info',    {'fields': ('name', 'phone', 'email', 'city', 'inquiry_type', 'plot_size', 'message')}),
        ('Admin',        {'fields': ('status', 'admin_note', 'assigned_to')}),
        ('Meta',         {'fields': ('source', 'id', 'created_at', 'updated_at')}),
    )

    # Quick status change from list view
    actions = ['mark_called', 'mark_converted', 'mark_closed']

    def mark_called(self, request, queryset):
        queryset.update(status='called')
    mark_called.short_description = 'Mark selected as Called'

    def mark_converted(self, request, queryset):
        queryset.update(status='converted')
    mark_converted.short_description = 'Mark selected as Converted'

    def mark_closed(self, request, queryset):
        queryset.update(status='closed')
    mark_closed.short_description = 'Mark selected as Closed'