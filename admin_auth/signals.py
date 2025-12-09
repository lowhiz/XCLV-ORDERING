from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.db.utils import OperationalError, ProgrammingError
import csv
import os
from django.contrib.auth.hashers import make_password

@receiver(post_migrate)
def load_admin_credentials(sender, **kwargs):
    """
    Signal handler that automatically loads admin credentials
    from a CSV file after migrations are completed.
    This ensures that admin accounts are preloaded into the database
    for initial setup.
    """
    if sender.name != "admin_auth":  
        return

    try:
        from .models import AdminUser

        # Path to admins.csv
        csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'admin.csv')

        # Only load if table exists and is empty
        if not AdminUser.objects.exists():
            with open(csv_path, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Create a new AdminUser entry if it doesn't already exist
                    # Hash the password using Django's make_password for security
                    AdminUser.objects.get_or_create(
                        admin_id=row['adminid'].strip(),
                        defaults={
                            'password': make_password(row['password'].strip())
                        }
                    )
    except (OperationalError, ProgrammingError):
        pass