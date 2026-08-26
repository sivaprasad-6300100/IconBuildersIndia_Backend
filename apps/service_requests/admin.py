from django.contrib import admin
from .models import ServiceType, ServiceRequest


@admin.register(ServiceType)
class ServiceTypeAdmin(admin.ModelAdmin):
    list_display   = ('label', 'key', 'pricing_mode', 'flat_price', 'price_per_sqft', 'is_active', 'order')
    list_editable  = ('pricing_mode', 'flat_price', 'price_per_sqft', 'is_active', 'order')
    prepopulated_fields = {'key': ('label',)}
    ordering = ('order', 'label')
    fieldsets = (
        (None, {'fields': ('label', 'key', 'description', 'icon', 'is_active', 'order')}),
        ('Pricing — fill only the field that matches the mode', {
            'fields': ('pricing_mode', 'flat_price', 'price_per_sqft'),
            'description': (
                "Flat Price = fixed ₹ amount regardless of area (e.g. Compound Wall Cleaning: ₹5,000). "
                "Price per sq.ft = ₹ rate × the area the customer enters (e.g. New Construction: ₹1,800/sq.ft)."
            ),
        }),
    )


@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display   = ('name', 'phone', 'service_type', 'area_sqft', 'estimated_price', 'status', 'source', 'created_at')
    list_filter    = ('status', 'service_type', 'source')
    search_fields  = ('name', 'phone', 'email', 'address')
    ordering       = ('-created_at',)
    readonly_fields = ('id', 'estimated_price', 'created_at', 'updated_at')

    fieldsets = (
        ('Contact',      {'fields': ('name', 'phone', 'email')}),
        ('Location',     {'fields': ('address', 'latitude', 'longitude')}),
        ('Requirement',  {'fields': ('service_type', 'area_sqft', 'requirement_text', 'estimated_price')}),
        ('Admin',        {'fields': ('status', 'admin_note', 'assigned_to')}),
        ('Meta',         {'fields': ('source', 'id', 'created_at', 'updated_at')}),
    )

    actions = ['mark_reviewed', 'mark_contacted', 'mark_converted', 'mark_closed']

    def mark_reviewed(self, request, queryset):
        queryset.update(status='reviewed')
    mark_reviewed.short_description = 'Mark selected as Reviewed'

    def mark_contacted(self, request, queryset):
        queryset.update(status='contacted')
    mark_contacted.short_description = 'Mark selected as Contacted'

    def mark_converted(self, request, queryset):
        queryset.update(status='converted')
    mark_converted.short_description = 'Mark selected as Converted'

    def mark_closed(self, request, queryset):
        queryset.update(status='closed')
    mark_closed.short_description = 'Mark selected as Closed'
