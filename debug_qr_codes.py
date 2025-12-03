import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xclv_ordering.settings')
django.setup()

from qr_codes.models import QRBatch, QRCode

def debug_qr_codes():
    # First, let's see what batches exist and which is active
    print("=== QR BATCHES ===")
    for batch in QRBatch.objects.all():
        status = "🟢 ACTIVE" if batch.batch_status else "🔴 Inactive"
        qr_count = batch.qr_codes.count()
        print(f"{batch.batch_name}: {status} ({qr_count} QR codes)")

    print("\n" + "="*50)

    # Get active batch QR codes
    active_batch = QRBatch.objects.filter(batch_status=True).first()
    if active_batch:
        print(f"\n=== ACTIVE BATCH: {active_batch.batch_name} ===")
        active_qrs = QRCode.objects.filter(batch=active_batch)[:3]  # Get first 3

        for qr in active_qrs:
            print(f"✅ VALID QR: {qr.unique_token}")
            print(f"   URL: http://127.0.0.1:8000/order/?qr={qr.qr_hash}")
            print(f"   Token: {qr.unique_token}")
            print()
    else:
        print("❌ No active batch found!")

    # Get inactive batch QR codes
    inactive_batch = QRBatch.objects.filter(batch_status=False).first()
    if inactive_batch:
        print(f"=== INACTIVE BATCH: {inactive_batch.batch_name} ===")
        inactive_qrs = QRCode.objects.filter(batch=inactive_batch)[:2]  # Get first 2

        for qr in inactive_qrs:
            print(f"❌ INVALID QR: {qr.unique_token}")
            print(f"   URL: http://127.0.0.1:8000/order/?qr={qr.qr_hash}")
            print(f"   Token: {qr.unique_token}")
            print()
    else:
        print("No inactive batches found!")

    print("\n" + "="*50)
    print("TESTING INSTRUCTIONS:")
    print("1. Copy a VALID QR URL - should pass QR validation, then ask for location")
    print("2. Copy an INVALID QR URL - should show 'QR Code Not Active' error")
    print("3. Try a fake hash - should show 'Invalid QR Code' error")
    print("   Example: http://127.0.0.1:8000/order/?qr=fakehash123")

if __name__ == "__main__":
    debug_qr_codes()
