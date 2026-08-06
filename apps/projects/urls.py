from django.urls import path
from .views import (
    ProjectListCreateView,
    ProjectDetailView,
    MilestoneListCreateView,
    MilestoneDetailView,
    ProjectAnalyticsView,
    MyProjectView,
    ClientPaymentListCreateView,
    ContractorPaymentListCreateView,
)

urlpatterns = [
    path('mine/', MyProjectView.as_view(), name='my-project'),
    path('', ProjectListCreateView.as_view(), name='project-list-create'),
    path('analytics/', ProjectAnalyticsView.as_view(), name='project-analytics'),
    path('<uuid:id>/', ProjectDetailView.as_view(), name='project-detail'),
    path('<uuid:project_id>/milestones/', MilestoneListCreateView.as_view(), name='milestone-list-create'),
    path('milestones/<uuid:id>/', MilestoneDetailView.as_view(), name='milestone-detail'),
    path('<uuid:project_id>/client-payments/', ClientPaymentListCreateView.as_view()),
    path('<uuid:project_id>/contractor-payments/', ContractorPaymentListCreateView.as_view()),
]