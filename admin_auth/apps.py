from django.apps import AppConfig
class AdminAuthConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'admin_auth'
    
    # To initialize the fixtures
    def ready(self):
        from . import signals