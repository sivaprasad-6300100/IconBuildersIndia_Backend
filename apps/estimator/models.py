from django.core.exceptions import ValidationError
from django.db import models


class EstimatorCity(models.Model):
    """One row per city — the base construction rate admin sets here drives
    the whole calculation for that city."""
    name = models.CharField(max_length=100, unique=True)
    rate_per_sqft = models.PositiveIntegerField(
        help_text="Base construction rate in ₹ per sq.ft for this city."
    )
    is_active = models.BooleanField(
        default=True, help_text="Untick to hide this city from the estimator without deleting it."
    )
    order = models.PositiveIntegerField(default=0, help_text="Lower numbers appear first.")

    class Meta:
        ordering = ['order', 'name']
        verbose_name = "City Rate"
        verbose_name_plural = "City Rates"

    def __str__(self):
        return f"{self.name} — ₹{self.rate_per_sqft}/sq.ft"


class EstimatorQualityTier(models.Model):
    """Basic / Standard / Premium / Luxury — each multiplies the base cost."""
    key = models.SlugField(
        max_length=50, unique=True,
        help_text="Internal id (e.g. 'basic'). Don't change this after creation — the frontend won't recognise a changed key."
    )
    label = models.CharField(max_length=100, help_text="Shown to the customer, e.g. 'Premium'.")
    multiplier = models.DecimalField(
        max_digits=4, decimal_places=2,
        help_text="Applied on top of the city's base rate. 1.00 = same as base rate, 1.70 = 70% more expensive."
    )
    description = models.CharField(
        max_length=255,
        help_text="What this tier contains, e.g. 'Designer finish, modular interiors'."
    )
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0, help_text="Lower numbers appear first, top to bottom.")

    class Meta:
        ordering = ['order']
        verbose_name = "Quality Tier"
        verbose_name_plural = "Quality Tiers"

    def __str__(self):
        return f"{self.label} (×{self.multiplier})"


class EstimatorAddOn(models.Model):
    """Optional extras like a swimming pool or interior design."""
    ICON_CHOICES = [
        ('wrench', 'Wrench'),
        ('sparkles', 'Sparkles'),
    ]
    label = models.CharField(max_length=100)
    cost = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Flat cost in ₹, regardless of plot size. Leave blank if using 'cost per sq.ft' instead."
    )
    cost_per_sqft = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="₹ per sq.ft of plot size — scales with the project. Leave blank if using 'flat cost' instead."
    )
    icon = models.CharField(max_length=20, choices=ICON_CHOICES, default='sparkles')
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name = "Add-on"
        verbose_name_plural = "Add-ons"

    def __str__(self):
        return self.label

    def clean(self):
        if not self.cost and not self.cost_per_sqft:
            raise ValidationError("Set either a flat cost or a cost per sq.ft — one of the two is required.")
        if self.cost and self.cost_per_sqft:
            raise ValidationError("Set only ONE of flat cost / cost per sq.ft, not both.")


class EstimatorConstructionType(models.Model):
    """Residential / Villa / Apartment / Commercial — each nudges cost up or down."""
    key = models.SlugField(max_length=50, unique=True, help_text="Internal id, don't change after creation.")
    label = models.CharField(max_length=100)
    adjustment_factor = models.DecimalField(
        max_digits=4, decimal_places=2, default=1.00,
        help_text="1.00 = no change, 1.15 = 15% more expensive than a standard residential build."
    )
    icon = models.CharField(
        max_length=20, default='building',
        choices=[('home', 'Home'), ('building', 'Building'), ('layers', 'Layers')],
    )
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name = "Construction Type"
        verbose_name_plural = "Construction Types"

    def __str__(self):
        return self.label


class EstimatorBreakdownItem(models.Model):
    """Cost breakdown shown on the result card — Structure, Finishing, etc.
    Percentages should sum to 1.00 across all active rows (validated below)."""
    label = models.CharField(max_length=100)
    percentage = models.DecimalField(
        max_digits=4, decimal_places=3,
        help_text="Share of base cost, e.g. 0.380 = 38%."
    )
    color_hex = models.CharField(
        max_length=7, default='#c9a84c',
        help_text="Bar color, e.g. #c9a84c"
    )
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name = "Breakdown Item"
        verbose_name_plural = "Breakdown Items"

    def __str__(self):
        return f"{self.label} ({self.percentage * 100}%)"


class EstimatorTimelineConfig(models.Model):
    """Singleton — controls the 'estimated timeline' formula:
    months = base_months + (floors * per_floor_months) + (plot_size / sqft_divisor)"""
    base_months = models.PositiveIntegerField(default=6)
    per_floor_months = models.DecimalField(max_digits=4, decimal_places=2, default=2.00)
    sqft_divisor = models.PositiveIntegerField(
        default=900,
        help_text="Plot size is divided by this number and added as months. Lower = longer timelines for big plots."
    )

    class Meta:
        verbose_name = "Timeline Formula"
        verbose_name_plural = "Timeline Formula"

    def save(self, *args, **kwargs):
        self.pk = 1  # enforce singleton
        super().save(*args, **kwargs)

    def __str__(self):
        return "Timeline Formula Settings"

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class EstimatorSpecCategory(models.Model):
    """Line-item categories reused across all tiers — Flooring, Paint, Doors,
    Windows, Kitchen, Electrical, etc. One shared list so the admin picks
    from the same categories no matter which tier they're editing."""
    name = models.CharField(max_length=100, unique=True)
    order = models.PositiveIntegerField(default=0, help_text="Lower numbers appear first.")

    class Meta:
        ordering = ['order', 'name']
        verbose_name = "Spec Category"
        verbose_name_plural = "Spec Categories"

    def __str__(self):
        return self.name


class EstimatorTierSpec(models.Model):
    """What a specific quality tier actually includes for a category —
    e.g. Premium → Flooring → 'Premium Vitrified / Marble',
    Basic → Flooring → 'Ceramic Tiles'.
    This is the piece that lets the frontend swap the included-items list
    when the customer changes Basic/Standard/Premium/Luxury."""
    tier = models.ForeignKey(
        EstimatorQualityTier, related_name='specs', on_delete=models.CASCADE
    )
    category = models.ForeignKey(EstimatorSpecCategory, on_delete=models.CASCADE)
    item_label = models.CharField(
        max_length=150,
        help_text="Shown to the customer, e.g. 'Premium Vitrified / Marble'."
    )

    class Meta:
        unique_together = ('tier', 'category')
        ordering = ['category__order']
        verbose_name = "Tier Spec Item"
        verbose_name_plural = "Tier Spec Items"

    def __str__(self):
        return f"{self.tier.label} — {self.category.name}: {self.item_label}"



class EstimatorFloorOption(models.Model):
    label = models.CharField(max_length=50, help_text="e.g. 'Ground', 'G+1', 'G+2'")
    floor_count = models.PositiveIntegerField(help_text="Numeric floor count used in the formula, e.g. 1, 2, 3")
    multiplier = models.DecimalField(
        max_digits=4, decimal_places=2, default=1.00,
        help_text="Cost multiplier for this many floors relative to single floor."
    )
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.label} (×{self.multiplier})"