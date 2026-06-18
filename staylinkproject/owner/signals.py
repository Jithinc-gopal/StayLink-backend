# owner/signals.py
# Signals are like event listeners in Django
# "When X happens, automatically do Y"

import httpx
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Property


@receiver(post_save, sender=Property)
def rebuild_ai_index_on_property_save(sender, instance, created, **kwargs):
    """
    Fires automatically every time a Property is saved or updated.
    
    Tells FastAPI to rebuild its ChromaDB index so the AI
    always has up-to-date property information.
    
    Uses try/except so if AI service is offline,
    Django still works normally — property still saves.
    """
    action = "created" if created else "updated"
    print(f"🏠 Property {action}: {instance.title} — notifying AI service...")

    try:
        httpx.post(
            "http://localhost:8001/rebuild-index",
            timeout=5.0
        )
        print("✅ AI index rebuild triggered")
    except Exception as e:
        # AI service being down must NOT break Django
        print(f"⚠️ Could not notify AI service: {e}")