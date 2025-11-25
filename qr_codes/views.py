from posixpath import curdir
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.conf import settings
from .models import QRCode, QRBatch
from tables.models import Table
from geolocation.models import LAT, LON, RADIUS_METERS # Get geofencing constants from geolocation app
from geolocation.services import GeolocationService  # custom geolocation service
import json
import re
from django.shortcuts import render, get_object_or_404
from qr_codes.models import QRCode
from tables.models import Table
from menu.views import open_menu
def validation(request):
    """
    STEP 1: Customer scans QR code.
    - Check if QR exists and belongs to an active batch.
    - If valid, retrieve or create its associated table.
    - Then render the menu page linked to that table.
    """

    token = request.GET.get('qr')

    # Case 1: Missing QR token
    if not token:
        return render(request, 'qr_codes/error.html', {
            'message': 'No QR code provided.'
        })

    try:
        # Retrieve QR code and its batch in one query
        qr_code = QRCode.objects.select_related('batch').get(qr_hash=token)
    except QRCode.DoesNotExist:
        # Case 2: QR code not found
        return render(request, 'qr_codes/error.html', {
            'message': 'Invalid or unknown QR code.'
        })

    # Case 3: Batch is inactive
    if not qr_code.batch.batch_status:
        return render(request, 'qr_codes/error.html', {
            'message': 'This QR code belongs to an inactive batch.'
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

            # Check if the pattern on the token (upon scanning) matches the one in the database
            token_pattern = re.compile(r"xclv-([a-zA-Z]+)-(\d+)-")
            match = token_pattern.search(qr_code.unique_token)

            if not match:
              return JsonResponse({
                  'success': False,
                  'error': 'Invalid QR code.'
              })

            # If successful, fetch table details
            # Extract category and number (e.g. "VIP" and "3") from the QR token
            category = match.group(1).upper()   # e.g. "VIP"
            number = match.group(2)             # e.g. "3"
            description = f"{category} {number}"  # e.g. "VIP 3"

            # Find or create the corresponding table
            table, created = Table.objects.get_or_create(
                description=description,
                defaults={
                    'qrcode': qr_code,
                    'total_payment': 0,
                    'table_status': True,
                }
            )

            # Store QR and table info in session
            request.session['active_table_id'] = table.id
            request.session['active_table_display'] = table.description
            request.session['active_qr_hash'] = qr_code.qr_hash

            return JsonResponse({
                'success': True,
                'message': 'Location validated successfully.',
                'redirect_url': f'/menu/view/?table_id={table.id}',
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

def toggle_batch(request):
    """
    Toggle the active QR batch.

    Rules:
    - Only one batch can be active at a time (batch_status=True).
    - If no batch is currently active, activate the first batch.
    - If a batch is active, deactivate it and activate the next batch in order.
    - The toggle is circular: after the last batch, it wraps back to the first.

    Steps:
    1. Get all batches ordered by ID.
    2. Find the currently active batch.
    3. If no batch is active, activate the first one.
    4. Otherwise, find the index of the current batch.
    5. Determine the next batch using modulo for circular rotation.
    6. Deactivate current batch and activate the next batch.
    """
    
    batches = list(QRBatch.objects.all().order_by('id'))
    if not batches:
        return

    # Find currently active batch
    current_batch = QRBatch.objects.filter(batch_status=True).first()

    if not current_batch:
        # If no batch is active yet, activate the first one
        first_batch = batches[0]
        first_batch.batch_status = True
        first_batch.save()

        # Automatically open the menu
        open_menu(True)
        return

    # Find index of the current active batch
    current_index = next((i for i, b in enumerate(batches) if b.id == current_batch.id), None)
    if current_index is None:
        return

    # Determine next batch (circular toggle)
    next_index = (current_index + 1) % len(batches)
    next_batch = batches[next_index]

    # Deactivate current and activate next
    current_batch.batch_status = False
    current_batch.save()

    next_batch.batch_status = True
    next_batch.save()
    open_menu(True)
    return redirect('qr_management')

def qr_management(request):

    # Get the global variable in /menu/views.py for the frontend implementation
    # of toggling between opening and closing the menu
    from menu.views import MENU_CLOSED

    # Get all of the batches in a list, retrieve the current batch, and init
    # next batch to none
    all_batches = QRBatch.objects.all().order_by('batch_name')
    batches = list(QRBatch.objects.all().order_by('id'))
    current_batch = QRBatch.objects.filter(batch_status=True).first()
    next_batch = None

    # Checks if there is a current batch and verifies if all the batches are in
    if current_batch and batches:
        # Find the current batch index
        current_index = next((i for i, b in enumerate(batches) if b.id == current_batch.id), None)

        # If it finds the current batch, get the next batch by batch[i+1]
        if current_index is not None:
            # Calculate next batch (circular)
            next_index = (current_index + 1) % len(batches)
            next_batch = batches[next_index]
    elif batches:
        # If no batch is active, the first batch would be next
        next_batch = batches[0]

    context = {
        'menu_closed': MENU_CLOSED,
        'batches': all_batches,
        'current_batch': current_batch,
        'next_batch': next_batch,
    }
    return render(request, 'qr_codes/management.html', context)
