from rest_framework import serializers

from .models import (
    EstimatorAddOn,
    EstimatorCity,
    EstimatorConstructionType,
    EstimatorQualityTier,
    EstimatorBreakdownItem,
    EstimatorTimelineConfig,
    EstimatorSpecCategory,
    EstimatorTierSpec,
    EstimatorFloorOption,
)


class EstimatorCitySerializer(serializers.ModelSerializer):
    class Meta:
        model = EstimatorCity
        fields = ['id', 'name', 'rate_per_sqft']


class EstimatorTierSpecSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = EstimatorTierSpec
        fields = ['id', 'category', 'item_label']


class EstimatorQualityTierSerializer(serializers.ModelSerializer):
    # Only active specs, in category order — this is the per-tier item list
    # (tiles, paint, doors...) shown to the customer when a tier is picked.
    specs = serializers.SerializerMethodField()

    class Meta:
        model = EstimatorQualityTier
        fields = ['id', 'key', 'label', 'multiplier', 'description', 'specs']

    def get_specs(self, obj):
        qs = obj.specs.select_related('category').order_by('category__order')
        return EstimatorTierSpecSerializer(qs, many=True).data


class EstimatorAddOnSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstimatorAddOn
        fields = ['id', 'label', 'cost', 'cost_per_sqft', 'icon']


class EstimatorConstructionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstimatorConstructionType
        fields = ['id', 'key', 'label', 'adjustment_factor', 'icon']


class EstimatorBreakdownItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstimatorBreakdownItem
        fields = ['id', 'label', 'percentage', 'color_hex']


class EstimatorTimelineConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstimatorTimelineConfig
        fields = ['base_months', 'per_floor_months', 'sqft_divisor']





# ── Admin write serializers (full field access, used by the new CRUD endpoints) ──

class EstimatorCityAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstimatorCity
        fields = ['id', 'name', 'rate_per_sqft', 'is_active', 'order']


class EstimatorQualityTierAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstimatorQualityTier
        fields = ['id', 'key', 'label', 'multiplier', 'description', 'is_active', 'order']


class EstimatorAddOnAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstimatorAddOn
        fields = ['id', 'label', 'cost', 'cost_per_sqft', 'icon', 'is_active', 'order']

    def validate(self, data):
        cost = data.get('cost', getattr(self.instance, 'cost', None))
        cost_per_sqft = data.get('cost_per_sqft', getattr(self.instance, 'cost_per_sqft', None))
        if not cost and not cost_per_sqft:
            raise serializers.ValidationError("Set either a flat cost or a cost per sq.ft.")
        if cost and cost_per_sqft:
            raise serializers.ValidationError("Set only ONE of flat cost / cost per sq.ft, not both.")
        return data


class EstimatorConstructionTypeAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstimatorConstructionType
        fields = ['id', 'key', 'label', 'adjustment_factor', 'icon', 'is_active', 'order']




class EstimatorSpecCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = EstimatorSpecCategory
        fields = ['id', 'name', 'order']


class EstimatorTierSpecAdminSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = EstimatorTierSpec
        fields = ['id', 'tier', 'category', 'category_name', 'item_label']
        read_only_fields = ['tier']



class EstimatorFloorOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstimatorFloorOption
        fields = ['id', 'label', 'floor_count', 'multiplier']


# Admin CRUD (used in the admin panel's manage view)
class EstimatorFloorOptionAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstimatorFloorOption
        fields = ['id', 'label', 'floor_count', 'multiplier', 'is_active', 'order']