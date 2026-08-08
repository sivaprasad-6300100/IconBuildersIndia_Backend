from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    EstimatorConfigView,
    EstimatorCityAdminViewSet,
    EstimatorQualityTierAdminViewSet,
    EstimatorAddOnAdminViewSet,
    EstimatorConstructionTypeAdminViewSet,
    EstimatorSpecCategoryAdminViewSet,
    EstimatorTierSpecAdminViewSet,   # ⬅️ was missing
    EstimatorFloorOptionAdminViewSet,
)

router = DefaultRouter()
router.register(r'admin/cities', EstimatorCityAdminViewSet, basename='estimator-admin-cities')
router.register(r'admin/quality-tiers', EstimatorQualityTierAdminViewSet, basename='estimator-admin-tiers')
router.register(r'admin/add-ons', EstimatorAddOnAdminViewSet, basename='estimator-admin-addons')
router.register(r'admin/construction-types', EstimatorConstructionTypeAdminViewSet, basename='estimator-admin-types')
router.register(r'admin/spec-categories', EstimatorSpecCategoryAdminViewSet, basename='estimator-admin-spec-categories')  # ⬅️ was missing
router.register(r'admin/tier-specs', EstimatorTierSpecAdminViewSet, basename='estimator-admin-tier-specs')  # ⬅️ was missing
router.register(r'admin/floor-options', EstimatorFloorOptionAdminViewSet, basename='estimator-admin-floor-options')  # ⬅️ add this

urlpatterns = [
    path('config/', EstimatorConfigView.as_view(), name='estimator-config'),
    path('', include(router.urls)),
]