from django.urls import path
from .views import (
    PortfolioProjectListView,
    PortfolioProjectDetailView,
    ProjectImageListView,
    PortfolioProjectAdminListCreateView,
    PortfolioProjectAdminDetailView,
    PortfolioBulkImageUploadView,
)

urlpatterns = [
    # Public — feeds the marketing site
    path('', PortfolioProjectListView.as_view(), name='portfolio-list'),
    path('<uuid:id>/', PortfolioProjectDetailView.as_view(), name='portfolio-detail'),
    path('<uuid:project_id>/images/', ProjectImageListView.as_view(), name='portfolio-images'),

    # Admin-only — used by the React Admin Panel
    path('admin/', PortfolioProjectAdminListCreateView.as_view(), name='portfolio-admin-list-create'),
    path('admin/<uuid:id>/', PortfolioProjectAdminDetailView.as_view(), name='portfolio-admin-detail'),
    path('admin/<uuid:project_id>/upload-images/', PortfolioBulkImageUploadView.as_view(), name='portfolio-admin-bulk-upload'),
]