from django.db.models import Sum, Avg, Count
from django.db.models.functions import TruncMonth
from django.utils import timezone
from datetime import timedelta
from rest_framework.response import Response


from apps.inquiries.models import Inquiry
from apps.portfolio.models import PortfolioProject

from rest_framework import generics, permissions
from apps.auth_app.permissions import IsAdmin
from .models import Project, Milestone
from .serializers import (
    ProjectListSerializer,
    ProjectDetailSerializer,
    ProjectCreateSerializer,
    MilestoneSerializer,
)


class ProjectListCreateView(generics.ListCreateAPIView):
    """
    Admin sees all projects.
    Client sees only their own projects.
    Contractor sees only projects assigned to them.
    Only admin can create.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ProjectCreateSerializer
        return ProjectListSerializer

    def get_queryset(self):
        user = self.request.user
        qs = Project.objects.filter(is_active=True)
        if user.role == 'client':
            return qs.filter(client=user)
        if user.role == 'contractor':
            return qs.filter(contractor=user)
        return qs  # admin sees all

    def perform_create(self, serializer):
        # only admin should reach here in practice; enforced via get_permissions
        serializer.save()

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdmin()]
        return [permissions.IsAuthenticated()]


class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve/update a single project.
    Client & contractor: read-only on their own project.
    Admin: full access.
    Delete = soft delete (is_active=False), never hard delete.
    """
    serializer_class = ProjectDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        user = self.request.user
        qs = Project.objects.all()
        if user.role == 'client':
            return qs.filter(client=user)
        if user.role == 'contractor':
            return qs.filter(contractor=user)
        return qs

    def get_permissions(self):
        if self.request.method in ('PUT', 'PATCH', 'DELETE'):
            return [IsAdmin()]
        return [permissions.IsAuthenticated()]

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()


class MilestoneListCreateView(generics.ListCreateAPIView):
    """Milestones for a given project (project_id passed in URL)."""
    serializer_class = MilestoneSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Milestone.objects.filter(project_id=self.kwargs['project_id'])

    def perform_create(self, serializer):
        serializer.save(project_id=self.kwargs['project_id'])

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdmin()]
        return [permissions.IsAuthenticated()]


class MilestoneDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Admin: update status/details.
    Contractor: can update status only (mark in_progress/completed) —
    enforce field-level restriction in serializer/frontend if needed.
    """
    queryset = Milestone.objects.all()
    serializer_class = MilestoneSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_permissions(self):
        if self.request.method == 'DELETE':
            return [IsAdmin()]
        return [permissions.IsAuthenticated()]









class ProjectAnalyticsView(generics.GenericAPIView):
    """Admin-only aggregated stats for the Analytics tab."""
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

    def get(self, request):
        projects = Project.objects.filter(is_active=True)

        total_revenue = projects.aggregate(total=Sum('amount_paid'))['total'] or 0
        avg_project_value = projects.aggregate(avg=Avg('total_budget'))['avg'] or 0

        total_inquiries = Inquiry.objects.count()
        converted = Inquiry.objects.filter(status='converted').count()
        conversion_rate = round((converted / total_inquiries) * 100, 1) if total_inquiries else 0

        # Revenue trend — last ~6 months, grouped by month of project creation
        six_months_ago = timezone.now() - timedelta(days=182)
        monthly = (
            projects.filter(created_at__gte=six_months_ago)
            .annotate(month=TruncMonth('created_at'))
            .values('month')
            .annotate(revenue=Sum('total_budget'))
            .order_by('month')
        )
        revenue_trend = [
            {
                'month': m['month'].strftime('%b'),
                'revenue': round(float(m['revenue'] or 0) / 100000, 1),  # in ₹ Lakhs
            }
            for m in monthly
        ]

        # Category split — from public Portfolio, not internal Project (no category field there)
        category_counts = (
            PortfolioProject.objects.values('category')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        total_portfolio = sum(c['count'] for c in category_counts) or 1
        category_split = [
            {'label': c['category'], 'pct': round((c['count'] / total_portfolio) * 100)}
            for c in category_counts
        ]

        return Response({
            'summary': {
                'total_revenue': float(total_revenue),
                'avg_project_value': float(avg_project_value),
                'conversion_rate': conversion_rate,
            },
            'revenue_trend': revenue_trend,
            'category_split': category_split,
        })