from django.urls import path
from .views import (
    ProjectListCreateView,
    ProjectDetailView,
    MilestoneListCreateView,
    MilestoneDetailView,
    ProjectAnalyticsView,
)

urlpatterns = [
    path('', ProjectListCreateView.as_view(), name='project-list-create'),
    path('analytics/', ProjectAnalyticsView.as_view(), name='project-analytics'),
    path('<uuid:id>/', ProjectDetailView.as_view(), name='project-detail'),
    path('<uuid:project_id>/milestones/', MilestoneListCreateView.as_view(), name='milestone-list-create'),
    path('milestones/<uuid:id>/', MilestoneDetailView.as_view(), name='milestone-detail'),
]