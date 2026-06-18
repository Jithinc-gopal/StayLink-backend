# staylinkproject/owner/apps.py
from django.apps import AppConfig

class OwnerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'owner'

    def ready(self):
        # Connect signals when Django starts
        # This makes the auto-index-rebuild work
        import owner.signals