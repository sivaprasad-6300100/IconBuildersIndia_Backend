from django.urls import path
from .views import ProjectPhotoListCreateView, ProjectPhotoDetailView

urlpatterns = [
    path('<uuid:project_id>/', ProjectPhotoListCreateView.as_view(), name='project-photo-list-create'),
    path('detail/<uuid:id>/', ProjectPhotoDetailView.as_view(), name='project-photo-detail'),
]