from rest_framework import serializers
from .models import Inquiry


class InquirySerializer(serializers.ModelSerializer):
    assigned_to_name = serializers.CharField(
        source='assigned_to.name', read_only=True, default=None
    )

    class Meta:
        model  = Inquiry
        fields = [
            'id', 'name', 'phone', 'email', 'city',
            'inquiry_type', 'plot_size', 'message',
            'status', 'admin_note', 'assigned_to', 'assigned_to_name',
            'source', 'created_at', 'updated_at','viewed_at', 
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CreateInquirySerializer(serializers.ModelSerializer):
    """Public form — anyone can submit"""
    class Meta:
        model  = Inquiry
        fields = [
            'name', 'phone', 'email', 'city',
            'inquiry_type', 'plot_size', 'message', 'source',
        ]

    def validate_phone(self, value):
        phone = value.replace(' ', '').replace('-', '')
        if len(phone) < 10:
            raise serializers.ValidationError('Enter a valid phone number')
        return value

    def validate_name(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError('Enter a valid name')
        return value.strip()


class UpdateInquiryStatusSerializer(serializers.Serializer):
    """Admin updates status + note"""
    status     = serializers.ChoiceField(choices=['new', 'called', 'converted', 'closed'])
    admin_note = serializers.CharField(required=False, allow_blank=True)