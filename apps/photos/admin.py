from django.contrib import admin
from .models import ProjectPhoto


@admin.register(ProjectPhoto)
class ProjectPhotoAdmin(admin.ModelAdmin):
    list_display = ('project', 'milestone', 'category', 'uploaded_by', 'is_active', 'created_at')
    list_filter = ('category', 'is_active')
    search_fields = ('project__name', 'caption')