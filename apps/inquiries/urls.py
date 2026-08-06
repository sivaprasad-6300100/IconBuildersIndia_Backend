from django.urls import path
from .views import (
    SubmitInquiryView,
    InquiryListView,
    InquiryDetailView,
    UpdateInquiryStatusView,
    MarkInquiriesViewedView,
)

urlpatterns = [
    # Public — contact form submission
    path('submit/',          SubmitInquiryView.as_view()),         # POST (public)

    # Admin only
    path('',                 InquiryListView.as_view()),           # GET all
    path('<uuid:pk>/',       InquiryDetailView.as_view()),         # GET / DELETE
    path('<uuid:pk>/status/',UpdateInquiryStatusView.as_view()),   # PATCH status
    path('mark-viewed/', MarkInquiriesViewedView.as_view(), name='mark-inquiries-viewed'),
]