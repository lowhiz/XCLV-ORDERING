# XCLV Davao Ordering System

This repository contains all source code and related resources for the **XCLV Davao Ordering System** project.

To better understand our **branching strategies**, **development workflow**, and overall **project context**, please visit the following links:

[Git and GitHub Documentation (by lowhiz)](https://docs.google.com/document/d/1l1XPDwYQddUXh0kjVJZButdPzNLvGjmAEwV0ho1QTAg/edit?usp=sharing)

[Project Document (in school domain)](https://docs.google.com/document/d/1AZlIi8WTghCwsrWWpuuY7iQlhgN1QCuq35Yy6cs11W0/edit?usp=sharing)

---

## 📘 Overview
The **XCLV Davao Ordering System** is being developed to streamline and simplify the ordering process for XCLV Davao.
It serves as a centralized platform for managing orders efficiently and securely.

---

## 🛠️ Tech Stack
- **Frontend:** HTML, CSS, JavaScript, Bootstrap
- **Backend:** Django (Python)
- **Database:** PostgreSQL
- **Version Control:** Git & GitHub

---

## 👥 Contributors
- [lowhiz](#)
- [luigi-ichi](#)
- [jcell](#)
- [jd](#)

## Development Onboarding
### Dependencies
- `pipenv` for managing Python virtual environments (installable via `pip install pipenv`)

### Onboarding Proper
- When working on the project, always run under the pipenv subshell. You can enter it by running `pipenv shell` in the project root directory.
 - The pipenv is a virtual environment containing all necessary dependencies for the project. This is to maintain consistency across different development environments The `Pipfile` lists all dependencies for the project in the event in the event that you prefer your local environment over pipenv.

### Testing
#### Prior to Running The Server
- Create a superuser account (if not already created) by running `python manage.py creates
- Ensure all migrations are applied by running `python manage.py migrate` within the pipenv shell.
- Follow the instructions in the [db-seeding/README.md](db-seeding/README.md) to seed the database with the pre-generated QR data.

#### Running The Server
- To run tests, use the command `python manage.py runserver` within the pipenv shell.
- To access the ordering form, you can generate test QR URLs. Simply execute `python manage.py shell` to enter the Django shell, then copy-paste and run the following code:
```python
from qr_codes.models import QRBatch, QRCode

# First, let's see what batches exist and which is active
print("=== QR BATCHES ===")
for batch in QRBatch.objects.all():
    status = "🟢 ACTIVE" if batch.is_active else "🔴 Inactive"
    qr_count = batch.qr_codes.count()
    print(f"{batch.batch_name}: {status} ({qr_count} QR codes)")

print("\n" + "="*50)

# Get active batch QR codes
active_batch = QRBatch.get_active_batch()
if active_batch:
    print(f"\n=== ACTIVE BATCH: {active_batch.batch_name} ===")
    active_qrs = QRCode.objects.filter(batch=active_batch)[:3]  # Get first 3

    for qr in active_qrs:
        print(f"✅ VALID QR: {qr.table_display_name}")
        print(f"   URL: http://127.0.0.1:8000/order/?qr={qr.qr_hash}")
        print(f"   Token: {qr.unique_token}")
        print()
else:
    print("❌ No active batch found!")

# Get inactive batch QR codes
inactive_batch = QRBatch.objects.filter(is_active=False).first()
if inactive_batch:
    print(f"=== INACTIVE BATCH: {inactive_batch.batch_name} ===")
    inactive_qrs = QRCode.objects.filter(batch=inactive_batch)[:2]  # Get first 2

    for qr in inactive_qrs:
        print(f"❌ INVALID QR: {qr.table_display_name}")
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
```



---

## 📄 License
This project is for educational purposes only and is maintained by the XCLV Davao development team.
