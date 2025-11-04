import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "admin_settings.settings")

app = Celery("admin_settings")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.conf.beat_schedule = {
    "every-5-seconds": {
        "task": "h5_backend.tasks.check_queue",
        "schedule": 5,
    },
}
app.conf.timezone = "UTC"

app.autodiscover_tasks()
