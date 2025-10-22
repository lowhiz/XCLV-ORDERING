from django.contrib import admin
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import GeofenceSettings, LocationCheck

# Register your models here.
#
@admin.register(GeofenceSettings)
class GeofenceSettingsAdmin(admin.ModelAdmin):
    """
    Custom admin for singleton GeofenceSettings
    Only allows editing, not adding or deleting
    """

    # Only show these fields
    fields = [
        'location_name',
        'latitude',
        'longitude',
        'radius_meters',
        'map_preview',
        'updated_at',
        'updated_by',
    ]

    readonly_fields = ['map_preview', 'updated_at', 'updated_by']

    list_display = [
        'location_name',
        'coordinates_display',
        'radius_display',
        'updated_at',
        'check_stats',
    ]

    def has_add_permission(self, request):
        """Disable adding new instances (singleton)"""
        return False

    def has_delete_permission(self, request, obj=None):
        """Disable deleting the instance (singleton)"""
        return False

    def changelist_view(self, request, extra_context=None):
        """
        Redirect changelist to the edit page of the singleton instance
        This ensures there's only ever one settings page
        """
        obj = GeofenceSettings.get_settings()
        return redirect('admin:geolocation_geofencesettings_change', obj.pk)

    def save_model(self, request, obj, form, change):
        """Track who updated the settings"""
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)
        messages.success(request, '✓ Geofence settings updated successfully!')

    def coordinates_display(self, obj):
        """Display coordinates with Google Maps link"""
        return format_html(
            '<a href="{}" target="_blank">{:.6f}, {:.6f}</a>',
            obj.get_google_maps_url(),
            obj.latitude,
            obj.longitude
        )
    coordinates_display.short_description = 'Coordinates'

    def radius_display(self, obj):
        """Display radius with formatting"""
        return format_html('<strong>{}m</strong>', obj.radius_meters)
    radius_display.short_description = 'Radius'

    def map_preview(self, obj):
        """Show embedded Google Maps preview"""
        if not obj.pk:
            return "Save to see map preview"

        return format_html(
            '''
            <div style="margin: 20px 0;">
                <iframe
                    width="100%"
                    height="400"
                    frameborder="0"
                    style="border:0; border-radius: 8px;"
                    src="https://www.google.com/maps?q={},{}&output=embed"
                    allowfullscreen>
                </iframe>
                <p style="margin-top: 10px;">
                    <a href="{}" target="_blank" class="button">
                        📍 Open in Google Maps
                    </a>
                </p>
            </div>
            ''',
            obj.latitude, obj.longitude,
            obj.get_google_maps_url()
        )
    map_preview.short_description = 'Location Preview'

    def check_stats(self, obj):
        """Show statistics about location checks"""
        total = LocationCheck.objects.count()
        inside = LocationCheck.objects.filter(is_inside=True).count()

        if total == 0:
            return "No checks yet"

        success_rate = (inside / total) * 100
        color = 'green' if success_rate > 80 else 'orange' if success_rate > 50 else 'red'

        return format_html(
            '<span style="color: {};">{:.1f}% success ({}/{})</span>',
            color, success_rate, inside, total
        )
    check_stats.short_description = 'Validation Stats'


@admin.register(LocationCheck)
class LocationCheckAdmin(admin.ModelAdmin):
    """Admin for viewing location check logs"""

    list_display = [
        'checked_at',
        'result_display',
        'distance_display',
        'user_location',
        'user_agent_short',
    ]

    list_filter = [
        'is_inside',
        'checked_at',
    ]

    search_fields = ['user_agent']

    readonly_fields = [
        'user_latitude',
        'user_longitude',
        'is_inside',
        'distance_meters',
        'geofence_latitude',
        'geofence_longitude',
        'geofence_radius',
        'user_agent',
        'checked_at',
    ]

    date_hierarchy = 'checked_at'

    def has_add_permission(self, request):
        """Can't manually add location checks"""
        return False

    def has_change_permission(self, request, obj=None):
        """Can only view, not edit"""
        return False

    def result_display(self, obj):
        """Show result with icon"""
        if obj.is_inside:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Inside</span>'
            )
        return format_html(
            '<span style="color: red; font-weight: bold;">✗ Outside</span>'
        )
    result_display.short_description = 'Result'

    def distance_display(self, obj):
        """Show formatted distance"""
        color = 'green' if obj.is_inside else 'red'
        return format_html(
            '<span style="color: {};">{}</span>',
            color, obj.formatted_distance
        )
    distance_display.short_description = 'Distance'

    def user_location(self, obj):
        """Show user location with map link"""
        return format_html(
            '<a href="https://www.google.com/maps?q={},{}" target="_blank">{:.6f}, {:.6f}</a>',
            obj.user_latitude, obj.user_longitude,
            obj.user_latitude, obj.user_longitude
        )
    user_location.short_description = 'User Location'

    def user_agent_short(self, obj):
        """Show shortened user agent"""
        if len(obj.user_agent) > 50:
            return obj.user_agent[:50] + "..."
        return obj.user_agent
    user_agent_short.short_description = 'Browser'
