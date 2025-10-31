from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.conf import settings
from .models import QRCode, QRBatch
from geolocation.models import LAT, LON, RADIUS_METERS # Get geofencing constants from geolocation app
from geolocation.services import GeolocationService  # custom geolocation service
import json


def validation(request):
    """
    STEP 1: Customer scans QR code.
    - Check if QR exists and belongs to an active batch.
    - If valid, render a page asking for geolocation permission.
    """
    token = request.GET.get('qr')

    # Case 1: Missing token in URL
    if not token:
        return render(request, {'message': 'No QR code provided.'})

    try:
        # Retrieve QR code and its batch relationship in one query
        qr_code = QRCode.objects.select_related('batch').get(qr_hash=token)

        # Case 2: Batch is inactive
        if not qr_code.batch.batch_status:
            return render(request, 'qr_codes/error.html', {
                'error_message': 'Invalid QR code.'
            })

        # Save QR temporarily in session for next step
        request.session['pending_qr_token'] = token
        request.session['pending_qr_id'] = qr_code.id

        # Step 3: Ask for geolocation (client-side JS will call validate_location_ajax)
        # @luigi-ichi, implement your geo-location here
        # >> Geolocation now implemented; template now points to its app template
        return render(request, 'geolocation/validate_location.html', {
            'qr_hash': token, # Gets from token declaration (line 18)
            'qr_code': qr_code   # Pass the qr_code object
        })

    except QRCode.DoesNotExist:
        # Case 3: QR code not found
        return render(request, 'error.html', {'message': 'Invalid QR code.'})


@csrf_exempt
def validate_location_ajax(request):
    """
    STEP 2: AJAX call from geolocation_prompt.html.
    - Receives user's coordinates and QR token.
    - Validates QR, batch status, and distance.
    - Returns JSON response (redirects to menu if successful).
    """
    try:
        data = json.loads(request.body)

        # Try multiple possible field names
        token = data.get('qr_token') or data.get('qr_hash') or data.get('qr')
        lat = data.get('latitude') or data.get('lat')
        lon = data.get('longitude') or data.get('lon') or data.get('lng')

        print(f"QR Hash: '{token}', Lat: '{lat}', Lon: '{lon}'")


        # Validate fields
        if not token or lat is None or lon is None:
            return JsonResponse({
                'success': False,
                'error': 'Missing required fields.'
            }, status=400)

        # Convert to float safely
        try:
            lat = float(lat)
            lon = float(lon)
        except ValueError:
            return JsonResponse({'success': False, 'error': 'Invalid coordinate format.'}, status=400)

        # Retrieve QR again
        qr_code = QRCode.objects.select_related('batch').get(qr_hash=token)

        # Ensure batch is still active
        if not qr_code.batch.batch_status:
            return JsonResponse({'success': False, 'error': 'Inactive batch.'}, status=403)

        # Check distance using your custom service
        # Retrieve geofencing constants from geolocation model
        distance = GeolocationService.calculate_distance(lat, lon, LAT, LON)

        # Use the constant radius from the geofencing constants
        if distance <= RADIUS_METERS:
            # Mark as validated in session
            request.session['validated_qr'] = token
            request.session['validation_time'] = timezone.now().isoformat()

            return JsonResponse({
                'success': True,
                'message': 'Location validated successfully.',
                'redirect_url': '/menu/',
                'distance': f"{distance:.1f} meters"
            })
        else:
            return JsonResponse({
                'success': False,
                'error': f'You are too far from the establishment ({distance:.1f} meters away).'
            })

    except QRCode.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Invalid QR code.'}, status=404)

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON format.'}, status=400)
