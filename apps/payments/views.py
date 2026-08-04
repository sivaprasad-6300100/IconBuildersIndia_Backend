from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

from apps.auth_app.permissions import IsAdmin
from apps.projects.models import Project
from .models import Payment
from .serializers import PaymentSerializer, CreatePaymentSerializer, MarkPaidSerializer


# ── List payments for a project ───────────────────────────────────────────────
class PaymentListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id):
        user = request.user

        # Get project based on role
        try:
            if user.role == 'admin':
                project = Project.objects.get(id=project_id)
            elif user.role == 'client':
                project = Project.objects.get(id=project_id, client=user)
            elif user.role == 'contractor':
                project = Project.objects.get(id=project_id, contractor=user)
            else:
                return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
        except Project.DoesNotExist:
            return Response({'error': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)

        payments = Payment.objects.filter(project=project)
        serializer = PaymentSerializer(payments, many=True)

        # Summary
        total_amount  = sum(p.amount for p in payments)
        total_paid    = sum(p.amount for p in payments if p.status == 'paid')
        total_pending = sum(p.amount for p in payments if p.status == 'pending')

        return Response({
            'payments': serializer.data,
            'summary': {
                'total_amount':  total_amount,
                'total_paid':    total_paid,
                'total_pending': total_pending,
            }
        })


# ── Admin creates a payment entry ─────────────────────────────────────────────
class CreatePaymentView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request, project_id):
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return Response({'error': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = CreatePaymentSerializer(data=request.data)
        if serializer.is_valid():
            payment = serializer.save(project=project, status='pending')
            return Response({
                'message': 'Payment entry created',
                'payment': PaymentSerializer(payment).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ── Admin marks payment as paid ───────────────────────────────────────────────
class MarkPaidView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def patch(self, request, payment_id):
        try:
            payment = Payment.objects.get(id=payment_id)
        except Payment.DoesNotExist:
            return Response({'error': 'Payment not found'}, status=status.HTTP_404_NOT_FOUND)

        if payment.status == 'paid':
            return Response({'error': 'Payment already marked as paid'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = MarkPaidSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Mark as paid
        payment.status       = 'paid'
        payment.paid_date    = serializer.validated_data['paid_date']
        payment.receipt_note = serializer.validated_data.get('receipt_note', '')
        payment.marked_by    = request.user

        if serializer.validated_data.get('method'):
            payment.method = serializer.validated_data['method']

        payment.save()

        # Update project amount_paid
        project = payment.project
        paid_total = Payment.objects.filter(
            project=project, status='paid'
        ).values_list('amount', flat=True)
        project.amount_paid = sum(paid_total)
        project.save()

        return Response({
            'message': f'Payment of ₹{payment.amount} marked as paid',
            'payment': PaymentSerializer(payment).data
        })


# ── Admin marks payment as pending again (undo) ───────────────────────────────
class MarkPendingView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def patch(self, request, payment_id):
        try:
            payment = Payment.objects.get(id=payment_id)
        except Payment.DoesNotExist:
            return Response({'error': 'Payment not found'}, status=status.HTTP_404_NOT_FOUND)

        payment.status       = 'pending'
        payment.paid_date    = None
        payment.receipt_note = ''
        payment.marked_by    = None
        payment.save()

        # Recalculate project amount_paid
        project = payment.project
        paid_total = Payment.objects.filter(
            project=project, status='paid'
        ).values_list('amount', flat=True)
        project.amount_paid = sum(paid_total)
        project.save()

        return Response({
            'message': 'Payment marked as pending',
            'payment': PaymentSerializer(payment).data
        })


# ── Delete payment entry (admin only) ─────────────────────────────────────────
class DeletePaymentView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def delete(self, request, payment_id):
        try:
            payment = Payment.objects.get(id=payment_id)
        except Payment.DoesNotExist:
            return Response({'error': 'Payment not found'}, status=status.HTTP_404_NOT_FOUND)

        payment.delete()
        return Response({'message': 'Payment deleted'}, status=status.HTTP_204_NO_CONTENT)