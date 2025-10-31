import re
from tables.models import Table
from qr_codes.models import QRCode, QRBatch

def initialize_tables(order):
    """
    Generate Table entries based only on the active batch's QR codes.
    """
    created = 0
    updated = 0
    token_pattern = re.compile(r"xclv-([a-zA-Z]+)-(\d+)-")

    qrcodes = QRCode.objects.filter(batch=active_batch)

    for qr in qrcodes:
        match = token_pattern.search(qr.unique_token)
        if not match:
            continue

        category = match.group(1).upper()
        number = match.group(2)
        description = f"{category} {number}"

        table, created_flag = Table.objects.update_or_create(
            qrcode=qr,
            defaults={
                "description": description,
                "total_payment": 0
            }
        )

        if created_flag:
            created += 1
        else:
            updated += 1

    return {
        "created": created,
        "updated": updated,
        "batch": active_batch.batch_name
    }
