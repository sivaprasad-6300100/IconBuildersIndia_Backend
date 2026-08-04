from rest_framework import serializers


class AdminLoginSerializer(serializers.Serializer):
    phone    = serializers.CharField(max_length=15)
    password = serializers.CharField(write_only=True)


class SendOTPSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=15)

    def validate_phone(self, value):
        phone = value.replace(' ', '').replace('-', '')
        if len(phone) < 10:
            raise serializers.ValidationError('Enter a valid phone number')
        return value


class VerifyOTPSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=15)
    otp   = serializers.CharField(max_length=6, min_length=6)

    def validate_otp(self, value):
        if not value.isdigit():
            raise serializers.ValidationError('OTP must be 6 digits')
        return value