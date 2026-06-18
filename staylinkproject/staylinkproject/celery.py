# staylinkproject/celery.py
import os
from celery import Celery

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "staylinkproject.settings"
)

app = Celery("staylinkproject")

app.config_from_object(
    "django.conf:settings",
    namespace="CELERY"
)

app.autodiscover_tasks()

# ← REMOVED app.conf.beat_schedule from here
# All scheduled tasks are now in settings.py
# under CELERY_BEAT_SCHEDULE