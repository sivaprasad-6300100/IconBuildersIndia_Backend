from rest_framework.permissions import AllowAny
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action

from .models import (
    EstimatorAddOn,
    EstimatorCity,
    EstimatorConstructionType,
    EstimatorQualityTier,
    EstimatorSpecCategory,
    EstimatorTierSpec,
    EstimatorFloorOption,
)
from .serializers import (
    EstimatorAddOnSerializer,
    EstimatorCitySerializer,
    EstimatorConstructionTypeSerializer,
    EstimatorConstructionTypeAdminSerializer,
    EstimatorQualityTierSerializer,
    EstimatorQualityTierAdminSerializer,
    EstimatorAddOnAdminSerializer,
    EstimatorCityAdminSerializer,
    EstimatorSpecCategorySerializer,
    EstimatorTierSpecAdminSerializer,
    EstimatorFloorOptionSerializer,        # ← add
    EstimatorFloorOptionAdminSerializer,   # ← add
)


class EstimatorConfigView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        quality_tiers = (
            EstimatorQualityTier.objects
            .filter(is_active=True)
            .prefetch_related('specs__category')
        )
        return Response({
            'cities': EstimatorCitySerializer(
                EstimatorCity.objects.filter(is_active=True), many=True
            ).data,
            'quality_tiers': EstimatorQualityTierSerializer(
                quality_tiers, many=True
            ).data,
            'add_ons': EstimatorAddOnSerializer(
                EstimatorAddOn.objects.filter(is_active=True), many=True
            ).data,
            'construction_types': EstimatorConstructionTypeSerializer(
                EstimatorConstructionType.objects.filter(is_active=True), many=True
            ).data,
            'floor_options': EstimatorFloorOptionSerializer(
                EstimatorFloorOption.objects.filter(is_active=True), many=True
            ).data,
        })


class IsAdminRole(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return bool(
            user and user.is_authenticated and (
                getattr(user, 'is_staff', False)
                or getattr(user, 'is_superuser', False)
                or getattr(user, 'role', None) == 'admin'
            )
        )


class EstimatorCityAdminViewSet(viewsets.ModelViewSet):
    queryset = EstimatorCity.objects.all().order_by('order', 'name')
    serializer_class = EstimatorCityAdminSerializer
    permission_classes = [IsAdminRole]


class EstimatorQualityTierAdminViewSet(viewsets.ModelViewSet):
    queryset = EstimatorQualityTier.objects.all().order_by('order')
    serializer_class = EstimatorQualityTierAdminSerializer
    permission_classes = [IsAdminRole]

    @action(detail=True, methods=['get', 'post'], url_path='specs')
    def specs(self, request, pk=None):
        tier = self.get_object()
        if request.method == 'GET':
            specs = tier.specs.select_related('category').order_by('category__order')
            return Response(EstimatorTierSpecAdminSerializer(specs, many=True).data)

        category_id = request.data.get('category')
        item_label = request.data.get('item_label', '').strip()
        if not category_id or not item_label:
            return Response({'detail': 'category and item_label are required.'}, status=400)

        spec, created = EstimatorTierSpec.objects.update_or_create(
            tier=tier, category_id=category_id,
            defaults={'item_label': item_label},
        )
        serializer = EstimatorTierSpecAdminSerializer(spec)
        return Response(serializer.data, status=201 if created else 200)


class EstimatorAddOnAdminViewSet(viewsets.ModelViewSet):
    queryset = EstimatorAddOn.objects.all().order_by('order')
    serializer_class = EstimatorAddOnAdminSerializer
    permission_classes = [IsAdminRole]


class EstimatorConstructionTypeAdminViewSet(viewsets.ModelViewSet):
    queryset = EstimatorConstructionType.objects.all().order_by('order')
    serializer_class = EstimatorConstructionTypeAdminSerializer
    permission_classes = [IsAdminRole]


class EstimatorFloorOptionAdminViewSet(viewsets.ModelViewSet):
    queryset = EstimatorFloorOption.objects.all().order_by('order')
    serializer_class = EstimatorFloorOptionAdminSerializer
    permission_classes = [IsAdminRole]


class EstimatorSpecCategoryAdminViewSet(viewsets.ModelViewSet):
    """Manage the shared category list (Flooring, Paint, Doors...) used across all tiers."""
    queryset = EstimatorSpecCategory.objects.all().order_by('order', 'name')
    serializer_class = EstimatorSpecCategorySerializer
    permission_classes = [IsAdminRole]


class EstimatorTierSpecAdminViewSet(viewsets.ModelViewSet):
    """Only used for DELETE/PATCH on individual spec rows."""
    queryset = EstimatorTierSpec.objects.all()
    serializer_class = EstimatorTierSpecAdminSerializer
    permission_classes = [IsAdminRole]


