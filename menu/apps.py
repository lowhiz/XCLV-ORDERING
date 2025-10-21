from django.apps import AppConfig
import csv
import os

class MenuConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'menu'

    def ready(self):
        from .models import Item

        csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'menu.csv')
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