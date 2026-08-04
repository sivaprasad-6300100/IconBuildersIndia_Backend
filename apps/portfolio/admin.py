from django.contrib import admin
from django.urls import path, reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.html import format_html
from django.contrib import messages

from .models import PortfolioProject, ProjectImage


class ProjectImageInline(admin.TabularInline):
    """Good for viewing/reordering a handful of images. For bulk adds,
    use the 'Bulk Upload Images' button on the project change page instead —
    Django admin's default inline can't handle 200+ file uploads well."""
    model = ProjectImage
    extra = 0
    fields = ('image', 'caption', 'order')


@admin.register(PortfolioProject)
class PortfolioProjectAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'category', 'status', 'progress',
        'image_count', 'is_published', 'order', 'bulk_upload_link',
    )
    list_filter = ('category', 'status', 'is_published')
    search_fields = ('title', 'location')
    inlines = [ProjectImageInline]

    def bulk_upload_link(self, obj):
        url = reverse('admin:portfolio-bulk-upload', args=[obj.id])
        return format_html('<a class="button" href="{}">Bulk Upload Images</a>', url)
    bulk_upload_link.short_description = 'Gallery'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<uuid:project_id>/bulk-upload/',
                self.admin_site.admin_view(self.bulk_upload_view),
                name='portfolio-bulk-upload',
            ),
        ]
        return custom_urls + urls

    def bulk_upload_view(self, request, project_id):
        project = get_object_or_404(PortfolioProject, id=project_id)

        if request.method == 'POST':
            files = request.FILES.getlist('images')
            if not files:
                messages.error(request, 'No files selected.')
            else:
                start_order = project.gallery_images.count()
                created = 0
                for i, f in enumerate(files):
                    ProjectImage.objects.create(
                        project=project,
                        image=f,
                        order=start_order + i,
                    )
                    created += 1
                messages.success(request, f'Uploaded {created} images to "{project.title}".')
                return redirect('admin:portfolio-bulk-upload', project_id=project.id)

        context = {
            **self.admin_site.each_context(request),
            'project': project,
            'existing_count': project.gallery_images.count(),
            'title': f'Bulk Upload Images — {project.title}',
        }
        return render(request, 'portfolio/bulk_upload.html', context)


@admin.register(ProjectImage)
class ProjectImageAdmin(admin.ModelAdmin):
    list_display = ('project', 'caption', 'order', 'created_at')
    list_filter = ('project',)
    search_fields = ('project__title', 'caption')