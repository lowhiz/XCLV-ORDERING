from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.db.utils import OperationalError, ProgrammingError
import csv
import os

@receiver(post_migrate)
def load_menu_items(sender, **kwargs):
    """
    Load menu items from menu.csv after migrations are completed.
    Only loads items if the table is empty.
    """
    if sender.name != "menu":  # Ensure it only runs for this app
        return

    try:
        from .models import Item

        # Path to menu.csv
        csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'menu.csv')

        # Only load if table exists and is empty
        if not Item.objects.exists():
            with open(csv_path, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    Item.objects.get_or_create(
                        name=row['name'].strip(),
                        defaults={
                            'description': row['description'].strip(),
                            'unit_price': row['unit_price'],
                            'category': row['category'].strip(),
                        }
                    )
    except (OperationalError, ProgrammingError):
        pass
