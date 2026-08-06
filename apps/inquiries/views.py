from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from apps.auth_app.permissions import IsAdmin
from .models import Inquiry
from .serializers import (
    InquirySerializer,
    CreateInquirySerializer,
    UpdateInquiryStatusSerializer,
)


# ── Public — anyone submits inquiry ──────────────────────────────────────────
class SubmitInquiryView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = CreateInquirySerializer(data=request.data)
        if serializer.is_valid():
            inquiry = serializer.save(status='new')
            return Response({
                'message': 'Inquiry submitted successfully! Our team will contact you within 24 hours.',
                'reference': str(inquiry.id)[:8].upper(),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ── Admin — list all inquiries ────────────────────────────────────────────────
class InquiryListView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        # Filter by status if provided
        filter_status = request.query_params.get('status')
        inquiries = Inquiry.objects.all()

        if filter_status:
            inquiries = inquiries.filter(status=filter_status)

        # Summary counts
        summary = {
            'total':     Inquiry.objects.count(),
            'new':       Inquiry.objects.filter(status='new').count(),
            'called':    Inquiry.objects.filter(status='called').count(),
            'converted': Inquiry.objects.filter(status='converted').count(),
            'closed':    Inquiry.objects.filter(status='closed').count(),
        }

        serializer = InquirySerializer(inquiries, many=True)
        return Response({
            'inquiries': serializer.data,
            'summary':   summary,
        })


# ── Admin — get single inquiry ────────────────────────────────────────────────
class InquiryDetailView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_object(self, pk):
        try:
            return Inquiry.objects.get(id=pk)
        except Inquiry.DoesNotExist:
            return None

    def get(self, request, pk):
        inquiry = self.get_object(pk)
        if not inquiry:
            return Response({'error': 'Inquiry not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(InquirySerializer(inquiry).data)

    def delete(self, request, pk):
        inquiry = self.get_object(pk)
        if not inquiry:
            return Response({'error': 'Inquiry not found'}, status=status.HTTP_404_NOT_FOUND)
        inquiry.delete()
        return Response({'message': 'Inquiry deleted'}, status=status.HTTP_204_NO_CONTENT)


# ── Admin — update inquiry status ─────────────────────────────────────────────
class UpdateInquiryStatusView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def patch(self, request, pk):
        try:
            inquiry = Inquiry.objects.get(id=pk)
        except Inquiry.DoesNotExist:
            return Response({'error': 'Inquiry not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = UpdateInquiryStatusSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        inquiry.status = serializer.validated_data['status']
        if serializer.validated_data.get('admin_note'):
            inquiry.admin_note = serializer.validated_data['admin_note']

        inquiry.save()

        return Response({
            'message': f'Inquiry status updated to {inquiry.status}',
            'inquiry': InquirySerializer(inquiry).data,
        })
    














from django.utils import timezone

# ── Admin — mark inquiries as viewed ──────────────────────────────────────────
class MarkInquiriesViewedView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request):
        ids = request.data.get('ids', [])
        if not ids:
            return Response({'error': 'No ids provided'}, status=status.HTTP_400_BAD_REQUEST)

        updated = Inquiry.objects.filter(
            id__in=ids,
            viewed_at__isnull=True
        ).update(viewed_at=timezone.now())

        return Response({'updated': updated})