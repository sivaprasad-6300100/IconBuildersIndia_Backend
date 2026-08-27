import uuid
from django.core.exceptions import ValidationError
from django.conf import settings
from django.db import models


class ServiceType(models.Model):
    """Admin-configured service categories a client can request on their land —
    e.g. Compound Wall Cleaning, Compound Wall Construction, Remodeling,
    New Construction, Repair & Maintenance.

    Admin picks, per service type, whether the price is a flat fee or scales
    with the area (sq.ft) the customer enters — mirrors the estimator app's
    'set one of the two' pattern.
    """

    PRICING_MODE_CHOICES = [
        ('flat', 'Flat Price'),
        ('per_sqft', 'Price per sq.ft'),
    ]
    ICON_CHOICES = [
        ('wall', 'Compound Wall'),
        ('home', 'Home'),
        ('building', 'Building'),
        ('wrench', 'Repair / Wrench'),
        ('paintbrush', 'Paint'),
        ('sparkles', 'Remodel / Sparkles'),
    ]

    key = models.SlugField(
        max_length=50, unique=True,
        help_text="Internal id (e.g. 'compound-wall-cleaning'). Don't change after creation."
    )
    label = models.CharField(
        max_length=150,
        help_text="Shown to the customer, e.g. 'Compound Wall Construction'."
    )
    description = models.CharField(
        max_length=255, blank=True, default='',
        help_text="Short helper text shown under the option, e.g. 'Boundary wall build or repair'."
    )
    pricing_mode = models.CharField(max_length=10, choices=PRICING_MODE_CHOICES, default='per_sqft')
    flat_price = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="₹ fixed amount. Used only when pricing mode is 'Flat Price'."
    )
    price_per_sqft = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="₹ per sq.ft, multiplied by the area the customer enters. Used only when pricing mode is 'Price per sq.ft'."
    )
    icon = models.CharField(max_length=20, choices=ICON_CHOICES, default='wall')
    is_active = models.BooleanField(
        default=True, help_text="Untick to hide this service from the request form without deleting it."
    )
    order = models.PositiveIntegerField(default=0, help_text="Lower numbers appear first.")

    class Meta:
        ordering = ['order', 'label']
        verbose_name = "Service Type"
        verbose_name_plural = "Service Types"

    def __str__(self):
        return self.label

    def clean(self):
        if self.pricing_mode == 'flat' and not self.flat_price:
            raise ValidationError("Set a flat price when pricing mode is 'Flat Price'.")
        if self.pricing_mode == 'per_sqft' and not self.price_per_sqft:
            raise ValidationError("Set a price per sq.ft when pricing mode is 'Price per sq.ft'.")

    def get_resolved_prices(self, city=None):
        """Returns (flat_price, price_per_sqft) — the city's override if one
        exists for this service, otherwise the service's own default."""
        flat_price, price_per_sqft = self.flat_price, self.price_per_sqft
        if city:
            override = self.city_prices.filter(city_name=city.strip().lower()).first()
            if override:
                if override.flat_price is not None:
                    flat_price = override.flat_price
                if override.price_per_sqft is not None:
                    price_per_sqft = override.price_per_sqft
        return flat_price, price_per_sqft

    def calculate_price(self, area_sqft=None, city=None):
        """Server-side price calculation — the price shown to the customer while
        they fill the form is a preview only; this is the number that's actually
        trusted and stored, so admin rate changes can never be bypassed by the client."""
        flat_price, price_per_sqft = self.get_resolved_prices(city)
        if self.pricing_mode == 'flat':
            return flat_price or 0
        if self.pricing_mode == 'per_sqft':
            if not area_sqft or area_sqft <= 0:
                return 0
            return round(float(price_per_sqft or 0) * float(area_sqft))
        return 0


class ServiceRequest(models.Model):
    """A guest-submitted request for property services: the client picks their
    land location (map pin + typed address), picks a service type, describes
    what they need, and gets a price back based on admin-configured rates.
    No login required. Lands in the admin panel, same pattern as Inquiry."""

    STATUS_CHOICES = [
        ('new',       'New'),
        ('reviewed',  'Reviewed'),
        ('contacted', 'Contacted'),
        ('converted', 'Converted'),
        ('closed',    'Closed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Contact — guest, no account needed
    name  = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)

    # Location — typed address plus an optional map pin
    address   = models.CharField(max_length=255, help_text="Typed address / plot details.")
    city      = models.CharField(max_length=100, blank=True, default='')
    latitude  = models.DecimalField(max_digits=12, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=12, decimal_places=6, null=True, blank=True)

    # Requirement
    service_type = models.ForeignKey(
        ServiceType, on_delete=models.PROTECT, related_name='requests'
    )
    area_sqft = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Only needed when the selected service type prices per sq.ft."
    )
    requirement_text = models.TextField(
        help_text="What the customer typed describing what they need done."
    )

    # Price — computed server-side at submit time from the admin's current
    # rates, then frozen on the request (so later rate changes don't retroactively
    # change what was quoted to this customer).
    estimated_price = models.PositiveIntegerField(default=0)

    # Admin tracking
    status      = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    admin_note  = models.TextField(blank=True)
    viewed_at   = models.DateTimeField(null=True, blank=True)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='assigned_service_requests'
    )

    # Source tracking
    source = models.CharField(max_length=50, default='website')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'service_requests'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} — {self.service_type.label} (₹{self.estimated_price})"



class ServiceTypeCityPrice(models.Model):
    """Per-city price override for a ServiceType. If no row exists for a given
    city, the ServiceType's own flat_price / price_per_sqft is used instead —
    so admin only adds a row for cities that differ from the default."""
    service_type = models.ForeignKey(
        ServiceType, related_name='city_prices', on_delete=models.CASCADE
    )
    city_name = models.CharField(
        max_length=100,
        help_text="Stored lowercase/trimmed automatically. Match the city as it appears from the map (e.g. 'Hyderabad')."
    )
    flat_price = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Overrides the flat price for this city. Leave blank to fall back to the default."
    )
    price_per_sqft = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Overrides the ₹/sq.ft rate for this city. Leave blank to fall back to the default."
    )

    class Meta:
        unique_together = ('service_type', 'city_name')
        ordering = ['city_name']
        verbose_name = "Service City Price"
        verbose_name_plural = "Service City Prices"

    def __str__(self):
        return f"{self.service_type.label} — {self.city_name}"

    def save(self, *args, **kwargs):
        self.city_name = self.city_name.strip().lower()
        super().save(*args, **kwargs)

    def clean(self):
        if self.flat_price is None and self.price_per_sqft is None:
            raise ValidationError("Set at least one of flat price / price per sq.ft for this city override.")