from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    ServiceTypeConfigView,
    SubmitServiceRequestView,
    ServiceTypeAdminViewSet,
    ServiceRequestListView,
    ServiceRequestDetailView,
    UpdateServiceRequestStatusView,
    MarkServiceRequestsViewedView,
    ServiceTypeCityPriceAdminViewSet,
)

router = DefaultRouter()
router.register(r'admin/service-types', ServiceTypeAdminViewSet, basename='service-requests-admin-types')

router.register(r'admin/city-prices', ServiceTypeCityPriceAdminViewSet, basename='service-requests-admin-city-prices')

urlpatterns = [
    # Public
    path('config/', ServiceTypeConfigView.as_view()),                      # GET service types + prices
    path('submit/', SubmitServiceRequestView.as_view()),                   # POST — guest submits

    # Admin
    path('', ServiceRequestListView.as_view()),                            # GET all
    path('<uuid:pk>/', ServiceRequestDetailView.as_view()),                # GET / DELETE
    path('<uuid:pk>/status/', UpdateServiceRequestStatusView.as_view()),   # PATCH status
    path('mark-viewed/', MarkServiceRequestsViewedView.as_view()),

    path('', include(router.urls)),
]
