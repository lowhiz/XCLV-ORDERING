from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.urls import reverse
from django.utils import timezone
import json

from .models import QRCode, QRBatch, ValidationAttempt
from .services import QRValidationService
from geolocation.services import GeolocationService


def order_entry(request):
    """
    Step 1: Customer scans QR code and lands here
    URL: /order?qr=abc123...

    - Extract hash from GET parameter
    - Check if QR exists
    - Check if belongs to active batch
    - Render validate_location.html for geolocation check
    """

    # Extract QR hash from URL parameter
    qr_hash = request.GET.get('qr')

    if not qr_hash:
        # No QR parameter provided
        return render(request, 'qr_codes/error.html', {
            'error_title': 'Invalid Access',
            'error_message': 'Please scan a valid QR code to access the ordering system.',
        })

    # Try to find the QR code
    qr_code = QRCode.get_by_hash(qr_hash)

    if not qr_code:
        # Log the invalid attempt
        ValidationAttempt.objects.create(
            qr_hash_attempted=qr_hash,
            result=ValidationAttempt.ResultChoices.QR_NOT_FOUND,
            error_message=f"QR hash '{qr_hash}' not found in database",
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            session_key=request.session.session_key or ''
        )

        return render(request, 'qr_codes/error.html', {
            'error_title': 'Invalid QR Code',
            'error_message': 'This QR code is not recognized. Please try scanning again or contact staff.',
        })

    # Check if QR code's batch is currently active
    if not qr_code.is_currently_valid:
        # Log the inactive batch attempt
        ValidationAttempt.objects.create(
            qr_code=qr_code,
            qr_hash_attempted=qr_hash,
            result=ValidationAttempt.ResultChoices.BATCH_INACTIVE,
            error_message=f"QR code belongs to inactive batch: {qr_code.batch.batch_name}",
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            session_key=request.session.session_key or ''
        )

        return render(request, 'qr_codes/error.html', {
            'error_title': 'QR Code Not Active',
            'error_message': 'This QR code is not currently active. Please contact staff or try a different QR code.',
        })

    # QR code is valid, now we need location validation
    # Store QR info in session for the AJAX validation
    request.session['pending_qr_hash'] = qr_hash
    request.session['pending_qr_id'] = qr_code.id

    # Get current table info if available (from tables app)
    table_info = None
    try:
        if hasattr(qr_code, 'tables') and qr_code.tables.exists():
            table_info = qr_code.tables.first()
    except:
        pass  # No table associated yet, that's fine

    # Render the location validation template
    context = {
        'qr_code': qr_code,
        'table_info': table_info,
        'qr_hash': qr_hash,
    }

    return render(request, 'qr_codes/validate_location.html', context)


@csrf_exempt
@require_http_methods(["POST"])
def validate_location_ajax(request):
    """
    Step 2: AJAX endpoint for location validation
    POST: /order/validate-location/

    - Receives: qr_hash, latitude, longitude
    - Uses QRValidationService.validate_entry()
    - Stores in session if valid
    - Returns JSON response
    """

    try:
        # Parse JSON data
        data = json.loads(request.body)
        qr_hash = data.get('qr_hash')
        latitude = data.get('latitude')
        longitude = data.get('longitude')

        # Validate required fields
        if not all([qr_hash, latitude, longitude]):
            return JsonResponse({
                'success': False,
                'error': 'Missing required fields: qr_hash, latitude, longitude'
            }, status=400)

        # Verify this matches the session
        session_qr_hash = request.session.get('pending_qr_hash')
        if session_qr_hash != qr_hash:
            return JsonResponse({
                'success': False,
                'error': 'Session mismatch. Please scan the QR code again.'
            }, status=400)

        # Use QRValidationService for complete validation
        result = QRValidationService.validate_entry(
            qr_hash=qr_hash,
            user_lat=float(latitude),
            user_lon=float(longitude),
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            session_key=request.session.session_key or ''
        )

        if result['success']:
            # SUCCESS - Valid QR and location
            qr_code = result['qr_code']

            # Store validated QR info in session
            request.session['validated_qr_id'] = qr_code.id
            request.session['validated_qr_hash'] = qr_hash
            request.session['validation_time'] = timezone.now().isoformat()

            # Clear pending data
            request.session.pop('pending_qr_hash', None)
            request.session.pop('pending_qr_id', None)

            return JsonResponse({
                'success': True,
                'message': 'Location validated successfully',
                'redirect_url': reverse('menu:menu_list'),  # Adjust based on your URL names
                'distance': f"{result['distance']:.0f}m" if result['distance'] < 1000 else f"{result['distance']/1000:.1f}km"
            })

        else:
            # FAILED validation
            return JsonResponse({
                'success': False,
                'error': result['error'],
                'result': result['result']
            })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)

    except ValueError as e:
        # Invalid latitude/longitude
        return JsonResponse({
            'success': False,
            'error': 'Invalid location coordinates'
        }, status=400)

    except Exception as e:
        # General error - log it
        ValidationAttempt.objects.create(
            qr_hash_attempted=qr_hash if 'qr_hash' in locals() else 'unknown',
            result=ValidationAttempt.ResultChoices.LOCATION_ERROR,
            error_message=f"Unexpected error: {str(e)}",
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            session_key=request.session.session_key or ''
        )

        return JsonResponse({
            'success': False,
            'error': 'An unexpected error occurred. Please try again.'
        }, status=500)


def get_client_ip(request):
    """Helper function to get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


# Legacy view for backward compatibility (if needed)
def validation(request):
    """
    Legacy validation view - redirects to new flow
    """
    token = request.GET.get('token')
    qr_hash = request.GET.get('qr')

    if qr_hash:
        # New flow with qr parameter
        return redirect(f"/order?qr={qr_hash}")
    elif token:
        # Legacy flow with token parameter - try to find matching QR
        try:
            qr_code = QRCode.objects.get(unique_token=token)
            return redirect(f"/order?qr={qr_code.qr_hash}")
        except QRCode.DoesNotExist:
            return render(request, 'qr_codes/error.html', {
                'error_title': 'Invalid Token',
                'error_message': 'This token is not recognized.',
            })
    else:
        return render(request, 'qr_codes/error.html', {
            'error_title': 'Missing Parameters',
            'error_message': 'Please scan a valid QR code.',
        })
