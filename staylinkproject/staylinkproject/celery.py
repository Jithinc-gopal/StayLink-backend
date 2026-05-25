import os
from celery import Celery
from celery.schedules import crontab   # ADD this import

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

# ============================================
# SCHEDULED TASKS
# Beat will fire these automatically
# ============================================

app.conf.beat_schedule = {

    # Runs every 15 minutes
    # Deletes expired OTP rows from EmailVerification table
    "cleanup-expired-otps": {
        "task": "accounts.tasks.cleanup_expired_otps_task",
        "schedule": crontab(minute="*/15"),
    },

}