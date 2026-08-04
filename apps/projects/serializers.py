from rest_framework import serializers
from .models import Project, Milestone


class MilestoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Milestone
        fields = [
            'id', 'project', 'title', 'description', 'order', 'status',
            'due_date', 'completed_date', 'amount', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProjectListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views."""
    client_name = serializers.CharField(source='client.name', read_only=True)
    contractor_name = serializers.CharField(source='contractor.name', read_only=True, default=None)
    progress_percent = serializers.ReadOnlyField()

    class Meta:
        model = Project
        fields = [
            'id', 'name', 'status', 'client', 'client_name',
            'contractor', 'contractor_name', 'total_budget', 'amount_paid',
            'progress_percent', 'is_active', 'created_at',
        ]


class ProjectDetailSerializer(serializers.ModelSerializer):
    """Full serializer with nested milestones."""
    milestones = MilestoneSerializer(many=True, read_only=True)
    balance_due = serializers.ReadOnlyField()
    progress_percent = serializers.ReadOnlyField()
    client_name = serializers.CharField(source='client.name', read_only=True)
    contractor_name = serializers.CharField(source='contractor.name', read_only=True, default=None)

    class Meta:
        model = Project
        fields = [
            'id', 'name', 'description', 'address',
            'client', 'client_name', 'contractor', 'contractor_name',
            'status', 'total_budget', 'amount_paid', 'balance_due',
            'start_date', 'expected_end_date', 'actual_end_date',
            'progress_percent', 'milestones', 'is_active',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'amount_paid', 'created_at', 'updated_at']



class ProjectCreateSerializer(serializers.ModelSerializer):
    """Used by admin to create a new project."""
    class Meta:
        model = Project
        fields = [
            'id', 'name', 'description', 'address', 'client', 'contractor',
            'status', 'total_budget', 'start_date', 'expected_end_date',
        ]
        read_only_fields = ['id']
