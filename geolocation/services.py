import math
from typing import Tuple, Optional
from .models import GeofenceSettings, LocationCheck

class GeolocationService:
    """
    Geolocation service for validating user locations
    Works with the singleton GeofenceSettings
    """

    @staticmethod
    def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate distance between two points using Haversine formula

        Argumentss:
            lat1, lon1: First point coordinates
            lat2, lon2: Second point coordinates

        Returns:
            Distance in meters
        """
        # Convert to radians
        lat1_rad = math.radians(float(lat1))
        lat2_rad = math.radians(float(lat2))
        lon1_rad = math.radians(float(lon1))
        lon2_rad = math.radians(float(lon2))

        # Haversine formula
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad

        a = (math.sin(dlat/2)**2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2)
        c = 2 * math.asin(math.sqrt(a))

        # Radius of Earth in meters
        radius = 6371000

        return radius * c

    @staticmethod
    def validate_location(
        user_lat: float,
        user_lon: float,
        log: bool = True,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Tuple[bool, float, Optional[LocationCheck]]:
        """
        Main validation method - checks if user is at the club location

        Arguments:
            user_lat, user_lon: User's coordinates
            log: Whether to log this check to database
            ip_address: User's IP (optional, but not stored)
            user_agent: User's browser info (optional)

        Returns:
            Tuple of (is_inside: bool, distance: float, log_entry: LocationCheck|None)
        """
        if not all([user_lat, user_lon]):
            return False, None, None

        # Get the singleton geofence settings
        settings = GeofenceSettings.get_settings()

        # Calculate distance
        distance = GeolocationService.calculate_distance(
            user_lat, user_lon,
            settings.latitude, settings.longitude
        )

        # Check if inside
        is_inside = distance <= settings.radius_meters

        # Log the check
        log_entry = None
        if log:
            log_entry = LocationCheck.objects.create(
                user_latitude=user_lat,
                user_longitude=user_lon,
                is_inside=is_inside,
                distance_meters=distance,
                geofence_latitude=settings.latitude,
                geofence_longitude=settings.longitude,
                geofence_radius=settings.radius_meters,
                user_agent=user_agent or '',
            )

        return is_inside, distance, log_entry
