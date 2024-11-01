"""
WSGI config for admin_settings project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

from django.core.wsgi import get_wsgi_application

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "admin_settings.settings")

application = get_wsgi_application()
