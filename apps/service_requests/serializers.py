from rest_framework import serializers

from .models import ServiceType, ServiceRequest, ServiceTypeCityPrice


# ── Public — feeds the request form's service picker + live price preview ─────
class ServiceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceType
        fields = [
            'id', 'key', 'label', 'description', 'icon',
            'pricing_mode', 'flat_price', 'price_per_sqft',
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        city = self.context.get('city')
        if city:
            flat_price, price_per_sqft = instance.get_resolved_prices(city)
            data['flat_price'] = flat_price
            data['price_per_sqft'] = price_per_sqft
        return data


# ── Admin write serializer (full field access, used by admin CRUD) ────────────
class ServiceTypeAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceType
        fields = [
            'id', 'key', 'label', 'description', 'icon',
            'pricing_mode', 'flat_price', 'price_per_sqft',
            'is_active', 'order',
        ]

    def validate(self, data):
        mode = data.get('pricing_mode', getattr(self.instance, 'pricing_mode', None))
        flat_price = data.get('flat_price', getattr(self.instance, 'flat_price', None))
        price_per_sqft = data.get('price_per_sqft', getattr(self.instance, 'price_per_sqft', None))
        if mode == 'flat' and not flat_price:
            raise serializers.ValidationError("Set a flat price when pricing mode is 'Flat Price'.")
        if mode == 'per_sqft' and not price_per_sqft:
            raise serializers.ValidationError("Set a price per sq.ft when pricing mode is 'Price per sq.ft'.")
        return data


# ── Admin — full read view of a submitted request ──────────────────────────────
class ServiceRequestSerializer(serializers.ModelSerializer):
    service_type_label = serializers.CharField(source='service_type.label', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.name', read_only=True, default=None)

    class Meta:
        model = ServiceRequest
        fields = [
            'id', 'name', 'phone', 'email',
            'address','city', 'latitude', 'longitude',
            'service_type', 'service_type_label', 'area_sqft', 'requirement_text',
            'estimated_price', 'status', 'admin_note',
            'assigned_to', 'assigned_to_name', 'source',
            'created_at', 'updated_at', 'viewed_at',
        ]
        read_only_fields = ['id', 'estimated_price', 'created_at', 'updated_at']


# ── Public form — anyone can submit, no login ──────────────────────────────────
class CreateServiceRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceRequest
        fields = [
            'name', 'phone', 'email',
            'address','city', 'latitude', 'longitude',
            'service_type', 'area_sqft', 'requirement_text', 'source',
        ]

    def validate_phone(self, value):
        phone = value.replace(' ', '').replace('-', '')
        if len(phone) < 10:
            raise serializers.ValidationError('Enter a valid phone number')
        return value

    def validate_name(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError('Enter a valid name')
        return value.strip()


    def validate(self, data):
        service_type = data.get('service_type')
        if service_type and service_type.pricing_mode == 'per_sqft' and not data.get('area_sqft'):
            raise serializers.ValidationError(
                {'area_sqft': "This service needs an area (sq.ft) to calculate the price."}
            )
    
        lat = data.get('latitude')
        lng = data.get('longitude')
        if lat is not None and lng is not None:
            if not (6.5 <= float(lat) <= 37.5 and 68.0 <= float(lng) <= 97.5):
                raise serializers.ValidationError(
                    {'address': "Location must be within India."}
                )
        return data

    def create(self, validated_data):
        service_type = validated_data['service_type']
        area_sqft = validated_data.get('area_sqft')
        city = validated_data.get('city')
        validated_data['estimated_price'] = service_type.calculate_price(area_sqft, city)
        return super().create(validated_data)


class UpdateServiceRequestStatusSerializer(serializers.Serializer):
    """Admin updates status + note"""
    status     = serializers.ChoiceField(choices=['new', 'reviewed', 'contacted', 'converted', 'closed'])
    admin_note = serializers.CharField(required=False, allow_blank=True)



class ServiceTypeCityPriceAdminSerializer(serializers.ModelSerializer):
    service_type_label = serializers.CharField(source='service_type.label', read_only=True)

    class Meta:
        model = ServiceTypeCityPrice
        fields = ['id', 'service_type', 'service_type_label', 'city_name', 'flat_price', 'price_per_sqft']

    def validate(self, data):
        flat_price = data.get('flat_price', getattr(self.instance, 'flat_price', None))
        price_per_sqft = data.get('price_per_sqft', getattr(self.instance, 'price_per_sqft', None))
        if flat_price is None and price_per_sqft is None:
            raise serializers.ValidationError("Set at least one of flat price / price per sq.ft.")
        return data