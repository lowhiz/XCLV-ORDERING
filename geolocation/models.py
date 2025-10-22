from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError

# Geofencing Constants
LAT = 7.093504776789317
LON = 125.61290047486922
RADIUS_METERS = 50

# Create your models here.

class GeofenceSettings(models.Model):
    """
    Singleton model - only ONE geofence for the entire system
    Stores the club's location boundaries
    """

    # Ensure only one instance of the geolocation exists
    class Meta:
        verbose_name = "Geofence Settings"
        verbose_name_plural = "Geofence Settings"

    # Location proper
    location_name = models.CharField(
        max_length=255,
        default="XCLV Club Davao",
        help_text="Name of the geofenced location"
    )

    # Center point coordinates
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        default=LAT,
        validators=[MinValueValidator(-90.0), MaxValueValidator(90.0)],
        help_text="Latitude of the geofenced location"
    )

    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        default=LON,
        validators=[MinValueValidator(-180.0), MaxValueValidator(180.0)],
        help_text="Longitude of the geofenced location"
    )

    # Radius of the center point
    radius_meters = models.PositiveIntegerField(
        default=RADIUS_METERS,
        help_text="Radius in meters for the geofenced area"
    )

    # Metadata for record keeping
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='geofence_updates'
    )

    def save(self, *args, **kwargs):
        if not self.pk and GeofenceSettings.objects.exists():
            # If trying to create a new instance when one already exists
            raise ValidationError('Only one GeofenceSettings instance is allowed. Please edit the existing one.')

        # Set pk to 1 to ensure singleton
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Prevent deletion of the singleton instance"""
        raise ValidationError('Cannot delete GeofenceSettings. You can only modify it.')

    @classmethod
    def get_settings(cls):
        """ Get the singleton instance, reate if it doesn't exist """
        obj, created = cls.objects.get_or_create(
            pk=1,
            defaults={
                'location_name': "XCLV Club Davao",
                'latitude': LAT,
                'longitude': LON,
                'radius_meters': RADIUS_METERS
            }
        )
        return obj

    def __str__(self):
            return f"{self.location_name} ({self.latitude}, {self.longitude}) - {self.radius_meters}m"

    def get_google_maps_url(self):
        """Generate Google Maps URL for this location"""
        return f"https://www.google.com/maps?q={self.latitude},{self.longitude}"

    def is_point_inside(self, lat, lon):
        """Check if a point is inside the geofence"""
        from .services import GeolocationService
        distance = GeolocationService.calculate_distance(
            lat, lon,
            self.latitude, self.longitude
        )
        return distance <= self.radius_meters, distance

class LocationCheck(models.Model):
    """
    Log all location validation attempts
    For analytics, debugging, and security
    """

    # User's location
    user_latitude = models.DecimalField(max_digits=9, decimal_places=6)
    user_longitude = models.DecimalField(max_digits=9, decimal_places=6)

    # Result
    is_inside = models.BooleanField(help_text="Was user inside geofence?")
    distance_meters = models.FloatField(help_text="Distance from geofence center in meters")

    # Geofence settings at time of check (for historical record)
    geofence_latitude = models.DecimalField(max_digits=9, decimal_places=6)
    geofence_longitude = models.DecimalField(max_digits=9, decimal_places=6)
    geofence_radius = models.IntegerField()

    # Metadata
    # ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    checked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-checked_at']
        verbose_name = 'Location Check'
        verbose_name_plural = 'Location Checks'
        indexes = [
            models.Index(fields=['-checked_at']),
            models.Index(fields=['is_inside', '-checked_at']),
        ]

    def __str__(self):
        status = "✓ Inside" if self.is_inside else "✗ Outside"
        return f"{status} - {self.distance_meters:.1f}m - {self.checked_at.strftime('%Y-%m-%d %H:%M')}"

    @property
    def formatted_distance(self):
            """Human-readable distance"""
            if self.distance_meters < 1000:
                return f"{self.distance_meters:.0f}m"
            else:
                return f"{self.distance_meters/1000:.1f}km"
