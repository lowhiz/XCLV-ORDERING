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
from menu.views import MENU_CLOSED

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
        return render(request, 'qr_invalid.html')

    try:
        # Retrieve QR code and its batch in one query
        qr_code = QRCode.objects.select_related('batch').get(qr_hash=token)
    except QRCode.DoesNotExist:
        # Case 2: QR code not found
        return render(request, 'qr_invalid.html')

    # Case 3: Batch is inactive
    if not qr_code.batch.batch_status:
        return render(request, 'qr_invalid.html')

    # Save QR temporarily in session for next step
    request.session['pending_qr_token'] = token
    request.session['pending_qr_id'] = qr_code.id

    # Step 3: Ask for geolocation (client-side JS will call validate_location_ajax)
    # @luigi-ichi, implement your geo-location here
    # >> Geolocation now implemented; template now points to its app template
    return render(request, 'validate_location.html', {
        'qr_hash': token, # Gets from token declaration (line 18)
        'qr_code': qr_code   # Pass the qr_code object
    })

@csrf_exempt
def validate_location_ajax(request):
    """
    STEP 2: AJAX call from validate_location.html.
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
        open_menu(request)
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
    open_menu(request)
    return redirect('qr_management')

def qr_management(request):
    return render(request, 'management.html')

# This code will show all the QR Code Batches together with their status
# Also retrieve the QR
def get_qr_status(request):
    batches = QRBatch.objects.all().order_by('id')

    batch_list = []
    menu_status = request.session.get("menu_closed", True)

    # Prepare a list of batch names for easier next-batch lookup
    batch_names = [batch.batch_name for batch in batches]

    active_batch = None
    next_batch = None
    for batch in batches:
        parts = batch.batch_name.split()
        batch_letter = parts[-1]          
        
        batch_list.append({
            "id": batch.id,                
            "letter": batch_letter,        
            "status": batch.batch_status,
        })

        if batch.batch_status:
            active_batch = batch.batch_name

        # Find the next batch
        if active_batch:
            active_index = batch_names.index(active_batch)
            if active_index + 1 < len(batch_names):
                next_batch = batch_names[active_index + 1]
            else:
                # Circular: loop back to the first batch
                next_batch = batch_names[0]
            
    return render(request, "qr_batches.html", {
        "batches": batch_list,
        "menu_closed": menu_status,
        "active_batch": active_batch,
        "next_batch": next_batch
    })

def qr_details(request, batch_id):
    batch = get_object_or_404(QRBatch, id=batch_id)
    qr_codes = batch.qr_codes.all()

    # In the original implemention, only image URLs were passed as qr_image_urls
    # This does not pass the table description needed to display on the page
    # We refactor qr_image_urls's loop...

    ## qr_image_urls = [code.image.url for code in qr_codes]  # code.image is the ImageField of each QR code url as a list, qr_codes

    #...to a list,

    ## qr_data = []

    # Where it will be passed as a context of both the image URL and the table
    # description that the template can call as qr_item.table_description,
    # assuming the loop is implemented as `for qr_item in qr_data`

    # Prepare QR code data with table labels
    qr_data = []
    token_pattern = re.compile(r"xclv-([a-zA-Z]+)-(\d+)-")

    for qr_code in qr_codes:
        match = token_pattern.search(qr_code.unique_token)

        if match:
            # Extract category and number from token
            category = match.group(1).upper()  # e.g., "ST", "VIP", "VVIP"
            number = match.group(2)            # e.g., "1", "2", "3"
            table_description = f"{category} {number}"  # e.g., "ST 1", "VIP 2"
        else:
            # Fallback if token doesn't match expected format
            table_description = f"QR {qr_code.id}"

        # For each index in the list contains both the image URL and table description
        qr_data.append({
            'qr_code': qr_code,
            'image_url': qr_code.image.url,
            'table_description': table_description,
        })

    return render(request, 'view_batch.html', {
        'batch': batch,
        'qr_data': qr_data, 
    })


def print_qr_codes(request, batch_id):
    batch = get_object_or_404(QRBatch, id=batch_id)
    qr_codes = batch.qr_codes.all()

    # Prepare QR code data with table labels
    qr_data = []
    token_pattern = re.compile(r"xclv-([a-zA-Z]+)-(\d+)-")

    for qr_code in qr_codes:
        match = token_pattern.search(qr_code.unique_token)

        if match:
            # Extract category and number from token
            category = match.group(1).upper()  # e.g., "ST", "VIP", "VVIP"
            number = match.group(2)            # e.g., "1", "2", "3"
            table_description = f"{category} {number}"  # e.g., "ST 1", "VIP 2"
        else:
            # Fallback if token doesn't match expected format
            table_description = f"Table {qr_code.id}"

        qr_data.append({
            'qr_code': qr_code,
            'image_url': qr_code.image.url,
            'table_description': table_description,
            'token': qr_code.unique_token
        })

    return render(request, 'print_qr_codes.html', {
        'batch': batch,
        'qr_data': qr_data,
        'total_codes': len(qr_data)
    })