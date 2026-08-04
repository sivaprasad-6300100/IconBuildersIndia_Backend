from rest_framework import serializers
from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    project_name  = serializers.CharField(source='project.name',    read_only=True)
    marked_by_name = serializers.CharField(source='marked_by.name', read_only=True, default=None)

    class Meta:
        model  = Payment
        fields = [
            'id', 'project', 'project_name',
            'milestone', 'milestone_name',
            'amount', 'method', 'status',
            'paid_date', 'receipt_note',
            'marked_by', 'marked_by_name',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'marked_by', 'created_at', 'updated_at']


class CreatePaymentSerializer(serializers.ModelSerializer):
    """Admin creates a payment entry for a project"""
    class Meta:
        model  = Payment
        fields = [
            'project', 'milestone', 'milestone_name',
            'amount', 'method',
        ]

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError('Amount must be greater than 0')
        return value


class MarkPaidSerializer(serializers.Serializer):
    """Admin marks a payment as paid"""
    paid_date    = serializers.DateField()
    receipt_note = serializers.CharField(max_length=500, required=False, allow_blank=True)
    method       = serializers.ChoiceField(
        choices=['cash', 'bank_transfer', 'upi', 'cheque'],
        required=False
    )