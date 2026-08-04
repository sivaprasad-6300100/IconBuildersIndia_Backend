from django.contrib import admin
from .models import Project, Milestone


class MilestoneInline(admin.TabularInline):
    model = Milestone
    extra = 0


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'client', 'contractor', 'status',
        'total_budget', 'amount_paid', 'is_active', 'created_at',
    )
    list_filter = ('status', 'is_active')
    search_fields = ('name', 'client__name', 'client__phone', 'contractor__name')
    inlines = [MilestoneInline]


@admin.register(Milestone)
class MilestoneAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'status', 'due_date', 'amount')
    list_filter = ('status',)
    search_fields = ('title', 'project__name')
