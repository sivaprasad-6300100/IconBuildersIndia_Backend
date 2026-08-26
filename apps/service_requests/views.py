from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from apps.auth_app.permissions import IsAdmin
from .models import ServiceType, ServiceRequest
from .serializers import (
    ServiceTypeSerializer,
    ServiceTypeAdminSerializer,
    ServiceRequestSerializer,
    CreateServiceRequestSerializer,
    UpdateServiceRequestStatusSerializer,
)


# ── Public — service types + admin-set prices, for the request form ──────────
class ServiceTypeConfigView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        types = ServiceType.objects.filter(is_active=True)
        return Response({
            'service_types': ServiceTypeSerializer(types, many=True).data,
        })


# ── Public — anyone submits a property service request, no login ─────────────
class SubmitServiceRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = CreateServiceRequestSerializer(data=request.data)
        if serializer.is_valid():
            req = serializer.save(status='new')
            return Response({
                'message': 'Request submitted successfully! Our team will contact you soon.',
                'reference': str(req.id)[:8].upper(),
                'estimated_price': req.estimated_price,
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ── Admin — manage service types (this is where prices are set) ──────────────
class ServiceTypeAdminViewSet(viewsets.ModelViewSet):
    queryset = ServiceType.objects.all().order_by('order', 'label')
    serializer_class = ServiceTypeAdminSerializer
    permission_classes = [IsAuthenticated, IsAdmin]


# ── Admin — list all submitted requests ───────────────────────────────────────
class ServiceRequestListView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        filter_status = request.query_params.get('status')
        reqs = ServiceRequest.objects.select_related('service_type', 'assigned_to').all()

        if filter_status:
            reqs = reqs.filter(status=filter_status)

        summary = {
            'total':     ServiceRequest.objects.count(),
            'new':       ServiceRequest.objects.filter(status='new').count(),
            'reviewed':  ServiceRequest.objects.filter(status='reviewed').count(),
            'contacted': ServiceRequest.objects.filter(status='contacted').count(),
            'converted': ServiceRequest.objects.filter(status='converted').count(),
            'closed':    ServiceRequest.objects.filter(status='closed').count(),
        }

        return Response({
            'requests': ServiceRequestSerializer(reqs, many=True).data,
            'summary': summary,
        })


# ── Admin — get / delete a single request ─────────────────────────────────────
class ServiceRequestDetailView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_object(self, pk):
        try:
            return ServiceRequest.objects.select_related('service_type', 'assigned_to').get(id=pk)
        except ServiceRequest.DoesNotExist:
            return None

    def get(self, request, pk):
        obj = self.get_object(pk)
        if not obj:
            return Response({'error': 'Request not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(ServiceRequestSerializer(obj).data)

    def delete(self, request, pk):
        obj = self.get_object(pk)
        if not obj:
            return Response({'error': 'Request not found'}, status=status.HTTP_404_NOT_FOUND)
        obj.delete()
        return Response({'message': 'Request deleted'}, status=status.HTTP_204_NO_CONTENT)


# ── Admin — update status ─────────────────────────────────────────────────────
class UpdateServiceRequestStatusView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def patch(self, request, pk):
        try:
            obj = ServiceRequest.objects.get(id=pk)
        except ServiceRequest.DoesNotExist:
            return Response({'error': 'Request not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = UpdateServiceRequestStatusSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        obj.status = serializer.validated_data['status']
        if serializer.validated_data.get('admin_note'):
            obj.admin_note = serializer.validated_data['admin_note']
        obj.save()

        return Response({
            'message': f'Request status updated to {obj.status}',
            'request': ServiceRequestSerializer(obj).data,
        })


# ── Admin — mark requests as viewed ───────────────────────────────────────────
class MarkServiceRequestsViewedView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request):
        ids = request.data.get('ids', [])
        if not ids:
            return Response({'error': 'No ids provided'}, status=status.HTTP_400_BAD_REQUEST)

        updated = ServiceRequest.objects.filter(
            id__in=ids,
            viewed_at__isnull=True
        ).update(viewed_at=timezone.now())

        return Response({'updated': updated})
