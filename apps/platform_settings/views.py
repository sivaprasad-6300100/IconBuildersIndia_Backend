from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status

from apps.auth_app.permissions import IsAdmin
from .models import PlatformSettings
from .serializers import PlatformSettingsSerializer


class PlatformSettingsView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

    def get(self, request):
        obj = PlatformSettings.load()
        return Response(PlatformSettingsSerializer(obj).data)

    def put(self, request):
        obj = PlatformSettings.load()
        serializer = PlatformSettingsSerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)