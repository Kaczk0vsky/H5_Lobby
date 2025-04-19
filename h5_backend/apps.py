from django.apps import AppConfig


class H5BackendConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "h5_backend"

    def ready(self):
        import h5_backend.signals
