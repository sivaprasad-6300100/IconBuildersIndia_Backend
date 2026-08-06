from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Django admin — superuser only
    path('django-admin/', admin.site.urls),

    # API routes
    path('api/auth/',      include('apps.auth_app.urls')),
    path('api/users/',     include('apps.users.urls')),
    path('api/projects/',  include('apps.projects.urls')),
    path('api/photos/',    include('apps.photos.urls')),
    path('api/payments/',  include('apps.payments.urls')),
    path('api/inquiries/', include('apps.inquiries.urls')),
    path('api/portfolio/', include('apps.portfolio.urls')),
    path('api/settings/', include('apps.platform_settings.urls')),
    path('api/notifications/', include('apps.notifications.urls')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)