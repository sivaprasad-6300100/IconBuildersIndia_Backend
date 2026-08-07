from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model  = User
        fields = ['id', 'phone', 'name', 'role', 'email', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class CreateClientSerializer(serializers.ModelSerializer):
    class Meta:
        model  = User
        fields = ['phone', 'name', 'email']

    def validate_phone(self, value):
        # Remove spaces and check length
        phone = value.replace(' ', '').replace('-', '')
        if len(phone) < 10:
            raise serializers.ValidationError('Enter a valid 10-digit phone number')
        if User.objects.filter(phone=phone).exists():
            raise serializers.ValidationError('This phone number is already registered')
        return phone
    
    def create(self, validated_data):
        request = self.context.get('request')
        user = User.objects.create_user(
            phone = validated_data['phone'],
            name  = validated_data['name'],
            role  = 'client',
        )
        if validated_data.get('email'):
            user.email = validated_data['email']
        if request and hasattr(user, 'created_by'):
            user.created_by = request.user
        user.save()
        return user


class CreateContractorSerializer(serializers.ModelSerializer):
    class Meta:
        model  = User
        fields = ['phone', 'name', 'email']

    def validate_phone(self, value):
        phone = value.replace(' ', '').replace('-', '')
        if len(phone) < 10:
            raise serializers.ValidationError('Enter a valid 10-digit phone number')
        if User.objects.filter(phone=phone).exists():
            raise serializers.ValidationError('This phone number is already registered')
        return phone

    def create(self, validated_data):
        request = self.context.get('request')
        user = User.objects.create_user(
            phone      = validated_data['phone'],
            name       = validated_data['name'],
            role       = 'contractor',
            # created_by = request.user if request else None,
        )
        if validated_data.get('email'):
            user.email = validated_data['email']
            user.save()
        return user


class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model  = User
        fields = ['name', 'phone', 'email', 'is_active']