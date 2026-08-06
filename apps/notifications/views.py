from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Notification
from .serializers import NotificationSerializer


# ── List notifications + unread count for the logged-in user ────────────────
class NotificationListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = Notification.objects.filter(user=request.user)
        serializer = NotificationSerializer(qs, many=True)
        return Response({
            'notifications': serializer.data,
            'unread_count': qs.filter(is_read=False).count(),
        })


# ── Mark all of the logged-in user's notifications as read ──────────────────
class MarkNotificationsReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        updated = Notification.objects.filter(
            user=request.user, is_read=False
        ).update(is_read=True)
        return Response({
            'message': f'{updated} notification(s) marked as read',
        })