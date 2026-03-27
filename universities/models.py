"""
University models for Chakula Poa.
"""
import uuid
from django.db import models


class University(models.Model):
    """University model."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=20, unique=True)  # e.g., "UDSM", "UDOM"
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)
    contact_phone = models.CharField(max_length=20, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'universities'
        verbose_name_plural = 'Universities'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.code})"
