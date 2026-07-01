import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault(
    'DJANGO_SETTINGS_MODULE',
    'staylinkproject.settings.dev'  # overridden by env var in production
)

application = get_wsgi_application()