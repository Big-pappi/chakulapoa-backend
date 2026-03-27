"""
Restaurant/Location models for Chakula Poa.
Supports all location types: universities, markets, offices, hospitals, industrial areas.
"""
import uuid
from django.db import models


class LocationType(models.TextChoices):
    """Location type choices."""
    RESTAURANT = 'restaurant', 'Restaurant'
    UNIVERSITY = 'university', 'University'
    MARKET = 'market', 'Market'
    OFFICE = 'office', 'Office'
    HOSPITAL = 'hospital', 'Hospital'
    INDUSTRIAL = 'industrial', 'Industrial'


# Tanzania regions
TANZANIA_REGIONS = [
    ('arusha', 'Arusha'),
    ('dar_es_salaam', 'Dar es Salaam'),
    ('dodoma', 'Dodoma'),
    ('geita', 'Geita'),
    ('iringa', 'Iringa'),
    ('kagera', 'Kagera'),
    ('katavi', 'Katavi'),
    ('kigoma', 'Kigoma'),
    ('kilimanjaro', 'Kilimanjaro'),
    ('lindi', 'Lindi'),
    ('manyara', 'Manyara'),
    ('mara', 'Mara'),
    ('mbeya', 'Mbeya'),
    ('morogoro', 'Morogoro'),
    ('mtwara', 'Mtwara'),
    ('mwanza', 'Mwanza'),
    ('njombe', 'Njombe'),
    ('pemba_north', 'Pemba North'),
    ('pemba_south', 'Pemba South'),
    ('pwani', 'Pwani'),
    ('rukwa', 'Rukwa'),
    ('ruvuma', 'Ruvuma'),
    ('shinyanga', 'Shinyanga'),
    ('simiyu', 'Simiyu'),
    ('singida', 'Singida'),
    ('songwe', 'Songwe'),
    ('tabora', 'Tabora'),
    ('tanga', 'Tanga'),
    ('zanzibar_north', 'Zanzibar North'),
    ('zanzibar_south', 'Zanzibar South'),
    ('zanzibar_west', 'Zanzibar West'),
]


class Restaurant(models.Model):
    """
    Restaurant/Location model.
    Represents any food service location across Tanzania.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=20, unique=True)  # e.g., "UDSM", "KARIAKOO-MKT"
    location_type = models.CharField(
        max_length=20,
        choices=LocationType.choices,
        default=LocationType.RESTAURANT
    )
    region = models.CharField(
        max_length=50,
        choices=TANZANIA_REGIONS,
        default='dar_es_salaam'
    )
    area = models.CharField(max_length=100, blank=True, null=True)  # e.g., "Mlimani City"
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)
    contact_phone = models.CharField(max_length=20, blank=True, null=True)
    capacity = models.PositiveIntegerField(default=0, help_text="Daily meal capacity")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'restaurants'
        verbose_name = 'Restaurant'
        verbose_name_plural = 'Restaurants'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    @property
    def location_type_display(self):
        return self.get_location_type_display()
    
    @property
    def region_display(self):
        return self.get_region_display()
