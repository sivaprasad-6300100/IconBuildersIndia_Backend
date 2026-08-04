from django.urls import path
from .views import (
    PaymentListView,
    CreatePaymentView,
    MarkPaidView,
    MarkPendingView,
    DeletePaymentView,
)

urlpatterns = [
    # List + create payments for a project
    path('project/<uuid:project_id>/',         PaymentListView.as_view()),    # GET
    path('project/<uuid:project_id>/create/',  CreatePaymentView.as_view()),  # POST (admin)

    # Mark paid / pending / delete
    path('<uuid:payment_id>/mark-paid/',        MarkPaidView.as_view()),       # PATCH (admin)
    path('<uuid:payment_id>/mark-pending/',     MarkPendingView.as_view()),    # PATCH (admin)
    path('<uuid:payment_id>/delete/',           DeletePaymentView.as_view()),  # DELETE (admin)
]