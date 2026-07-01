import os
from celery import Celery

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "staylinkproject.settings.dev"  # overridden by env var in production
)

app = Celery("staylinkproject")

app.config_from_object(
    "django.conf:settings",
    namespace="CELERY"
)

app.autodiscover_tasks()

# All scheduled tasks are in settings/base.py under CELERY_BEAT_SCHEDULE
# Nothing needed here