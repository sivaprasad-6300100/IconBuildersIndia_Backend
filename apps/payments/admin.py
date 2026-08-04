from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display   = ['project', 'milestone_name', 'amount', 'method', 'status', 'paid_date', 'marked_by']
    list_filter    = ['status', 'method']
    search_fields  = ['project__name', 'milestone_name', 'receipt_note']
    ordering       = ['-created_at']
    readonly_fields = ['id', 'created_at', 'updated_at']

    fieldsets = (
        ('Project',  {'fields': ('project', 'milestone', 'milestone_name')}),
        ('Payment',  {'fields': ('amount', 'method', 'status')}),
        ('Admin',    {'fields': ('paid_date', 'receipt_note', 'marked_by')}),
        ('System',   {'fields': ('id', 'created_at', 'updated_at')}),
    )