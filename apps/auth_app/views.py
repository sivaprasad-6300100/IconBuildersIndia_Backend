from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

from apps.users.models import User
from apps.users.serializers import UserSerializer
from .serializers import AdminLoginSerializer, SendOTPSerializer, VerifyOTPSerializer
from .otp_service import send_otp, verify_otp


# ── Helper: Generate JWT tokens ───────────────────────────────────────────────
def get_tokens(user):
    refresh = RefreshToken.for_user(user)
    refresh['role']  = user.role
    refresh['name']  = user.name
    refresh['phone'] = user.phone
    return {
        'access':  str(refresh.access_token),
        'refresh': str(refresh),
    }


# ── Admin Login — phone + password ────────────────────────────────────────────
class AdminLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = AdminLoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        phone    = serializer.validated_data['phone'].replace(' ', '').replace('-', '')
        password = serializer.validated_data['password']

        user = authenticate(request, username=phone, password=password)

        if not user:
            return Response(
                {'error': 'Invalid phone or password'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        if not user.is_active:
            return Response(
                {'error': 'Account is deactivated'},
                status=status.HTTP_403_FORBIDDEN
            )
        if user.role != 'admin':
            return Response(
                {'error': 'Access denied. Admin only.'},
                status=status.HTTP_403_FORBIDDEN
            )

        tokens = get_tokens(user)
        return Response({
            'message': f'Welcome {user.name}!',
            'user':    UserSerializer(user).data,
            'tokens':  tokens,
        }, status=status.HTTP_200_OK)


# ── Send OTP — Client & Contractor ────────────────────────────────────────────
class SendOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SendOTPSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        phone = serializer.validated_data['phone']

        # Clean phone
        clean_phone = phone.replace(' ', '').replace('-', '')
        if not clean_phone.startswith('91'):
            clean_phone = '91' + clean_phone

        # Check if registered
        user = None
        try:
            user = User.objects.get(phone=clean_phone)
        except User.DoesNotExist:
            try:
                user = User.objects.get(phone=phone.replace(' ', ''))
            except User.DoesNotExist:
                return Response(
                    {'error': 'Phone number not registered. Please contact admin.'},
                    status=status.HTTP_404_NOT_FOUND
                )

        if not user.is_active:
            return Response(
                {'error': 'Your account is deactivated. Contact admin.'},
                status=status.HTTP_403_FORBIDDEN
            )
        if user.role == 'admin':
            return Response(
                {'error': 'Admins use password login, not OTP.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Send OTP
        result = send_otp(phone)
        response_data = {
            'message': result['message'],
            'phone':   phone,
        }
        if result.get('dev_otp'):
            response_data['dev_otp'] = result['dev_otp']

        return Response(response_data, status=status.HTTP_200_OK)


# ── Verify OTP — Client & Contractor ─────────────────────────────────────────
class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        phone = serializer.validated_data['phone']
        otp   = serializer.validated_data['otp']

        # Verify OTP
        result = verify_otp(phone, otp)
        if not result['success']:
            return Response(
                {'error': result['message']},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get user
        clean_phone = phone.replace(' ', '').replace('-', '')
        if not clean_phone.startswith('91'):
            clean_phone = '91' + clean_phone

        user = None
        try:
            user = User.objects.get(phone=clean_phone)
        except User.DoesNotExist:
            try:
                user = User.objects.get(phone=phone.replace(' ', ''))
            except User.DoesNotExist:
                return Response(
                    {'error': 'User not found'},
                    status=status.HTTP_404_NOT_FOUND
                )

        tokens = get_tokens(user)
        return Response({
            'message': f'Welcome {user.name}!',
            'user':    UserSerializer(user).data,
            'tokens':  tokens,
        }, status=status.HTTP_200_OK)


# ── Get current logged in user ────────────────────────────────────────────────
class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            'user': UserSerializer(request.user).data
        })


# ── Logout ────────────────────────────────────────────────────────────────────
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Logged out successfully'})
        except Exception:
            return Response({'message': 'Logged out'})