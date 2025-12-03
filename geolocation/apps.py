from django.apps import AppConfig


class GeolocationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "geolocation"
    verbose_name = "Geolocation"

    def ready(self):
        """Initialize singleton geofence settings on startup"""
        # Ensure the singleton instance exists
        # This runs when Django starts
        pass  # The get_or_create in get_settings() handles this
