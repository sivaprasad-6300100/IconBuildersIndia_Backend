from rest_framework import serializers
from .models import Project, Milestone
from django.db.models import Sum
from .models import Project, Milestone, ClientPayment, ContractorPayment

class MilestoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Milestone
        fields = [
            'id', 'project', 'title', 'description', 'order', 'status',
            'due_date', 'completed_date', 'amount', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id','project', 'created_at', 'updated_at']

class ClientPaymentSerializer(serializers.ModelSerializer):
    logged_by_name = serializers.CharField(source='logged_by.name', read_only=True, default=None)

    class Meta:
        model = ClientPayment
        fields = ['id', 'project', 'amount', 'date', 'proof_image', 'logged_by', 'logged_by_name', 'created_at']
        read_only_fields = ['id','project', 'logged_by', 'created_at']


class ContractorPaymentSerializer(serializers.ModelSerializer):
    logged_by_name = serializers.CharField(source='logged_by.name', read_only=True, default=None)

    class Meta:
        model = ContractorPayment
        fields = ['id', 'project', 'amount', 'date', 'proof_image', 'logged_by', 'logged_by_name', 'created_at']
        read_only_fields = ['id','project', 'logged_by', 'created_at']




class ProjectListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views."""
    client_name = serializers.CharField(source='client.name', read_only=True)
    contractor_name = serializers.CharField(source='contractor.name', read_only=True, default=None)
    progress_percent = serializers.ReadOnlyField()
    contractor_paid = serializers.SerializerMethodField()  # ADD

    def get_contractor_paid(self, obj):
        return sum(p.amount for p in obj.contractor_payments.all())

    class Meta:
        model = Project
        fields = [
            'id', 'name', 'status', 'client', 'client_name',
            'contractor', 'contractor_name', 'total_budget', 'amount_paid',
            'contractor_fee', 'contractor_paid',
            'progress_percent', 'is_active', 'created_at',
        ]


class ProjectDetailSerializer(serializers.ModelSerializer):
    """Full serializer with nested milestones."""
    milestones = MilestoneSerializer(many=True, read_only=True)
    client_payments = ClientPaymentSerializer(many=True, read_only=True)      # ADD
    contractor_payments = ContractorPaymentSerializer(many=True, read_only=True)  # ADD
    site_photos = serializers.SerializerMethodField()  # ADD — client/contractor site photos for this project
    balance_due = serializers.ReadOnlyField()
    progress_percent = serializers.ReadOnlyField()
    client_name = serializers.CharField(source='client.name', read_only=True)
    contractor_name = serializers.CharField(source='contractor.name', read_only=True, default=None)

    def get_site_photos(self, obj):
        from apps.photos.serializers import ProjectPhotoSerializer
        photos = obj.photos.filter(is_active=True).order_by('-created_at')
        return ProjectPhotoSerializer(photos, many=True, context=self.context).data

    class Meta:
        model = Project
        fields = [
            'id', 'name', 'description', 'address',
            'client', 'client_name', 'contractor', 'contractor_name',
            'status', 'total_budget', 'amount_paid', 'balance_due','contractor_fee',
            'start_date', 'expected_end_date', 'actual_end_date',
            'progress_percent', 'milestones', 'is_active','client_payments', 'contractor_payments',
            'site_photos',
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