from django.contrib import admin

from .models import (
    EstimatorAddOn,
    EstimatorCity,
    EstimatorConstructionType,
    EstimatorQualityTier,
    EstimatorBreakdownItem,
    EstimatorTimelineConfig,
    EstimatorSpecCategory,
    EstimatorTierSpec,
    EstimatorFloorOption,
)


@admin.register(EstimatorCity)
class EstimatorCityAdmin(admin.ModelAdmin):
    list_display = ('name', 'rate_per_sqft', 'is_active', 'order')
    list_editable = ('rate_per_sqft', 'is_active', 'order')
    search_fields = ('name',)
    ordering = ('order', 'name')


@admin.register(EstimatorSpecCategory)
class EstimatorSpecCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'order')
    list_editable = ('order',)
    search_fields = ('name',)
    ordering = ('order',)


class EstimatorTierSpecInline(admin.TabularInline):
    model = EstimatorTierSpec
    extra = 1
    autocomplete_fields = ['category']


@admin.register(EstimatorQualityTier)
class EstimatorQualityTierAdmin(admin.ModelAdmin):
    list_display = ('label', 'key', 'multiplier', 'description', 'is_active', 'order')
    list_editable = ('multiplier', 'is_active', 'order')
    prepopulated_fields = {'key': ('label',)}
    ordering = ('order',)
    inlines = [EstimatorTierSpecInline]
    fieldsets = (
        (None, {
            'fields': ('label', 'key', 'multiplier', 'description', 'is_active', 'order'),
            'description': (
                "Multiplier is applied on top of the city's base rate. "
                "e.g. 1.30 means this tier costs 30% more than a multiplier of 1.00. "
                "Use the 'Tier Spec Item' rows below to set what this tier actually "
                "includes for each category (Flooring, Paint, Doors...) — that's what "
                "shows on the customer-facing page."
            ),
        }),
    )


@admin.register(EstimatorAddOn)
class EstimatorAddOnAdmin(admin.ModelAdmin):
    list_display = ('label', 'cost', 'cost_per_sqft', 'icon', 'is_active', 'order')
    list_editable = ('cost', 'cost_per_sqft', 'is_active', 'order')
    ordering = ('order',)
    fieldsets = (
        (None, {'fields': ('label', 'icon', 'is_active', 'order')}),
        ('Pricing — fill only ONE of these two', {
            'fields': ('cost', 'cost_per_sqft'),
            'description': (
                "Flat cost = fixed ₹ amount regardless of plot size (e.g. Swimming Pool: ₹8,00,000). "
                "Cost per sq.ft = scales with plot size (e.g. Interior Design: ₹350/sq.ft)."
            ),
        }),
    )


@admin.register(EstimatorConstructionType)
class EstimatorConstructionTypeAdmin(admin.ModelAdmin):
    list_display = ('label', 'key', 'adjustment_factor', 'is_active', 'order')
    list_editable = ('adjustment_factor', 'is_active', 'order')
    prepopulated_fields = {'key': ('label',)}
    ordering = ('order',)


@admin.register(EstimatorBreakdownItem)
class EstimatorBreakdownItemAdmin(admin.ModelAdmin):
    list_display = ['label', 'percentage', 'color_hex', 'is_active', 'order']
    list_editable = ['percentage', 'is_active', 'order']


@admin.register(EstimatorTimelineConfig)
class EstimatorTimelineConfigAdmin(admin.ModelAdmin):
    list_display = ['base_months', 'per_floor_months', 'sqft_divisor']

    def has_add_permission(self, request):
        # Singleton — block creating a second row
        return not EstimatorTimelineConfig.objects.exists()



@admin.register(EstimatorFloorOption)
class EstimatorFloorOptionAdmin(admin.ModelAdmin):
    list_display = ['label', 'floor_count', 'multiplier', 'is_active', 'order']
    list_editable = ['floor_count', 'multiplier', 'is_active', 'order']