from django.apps import AppConfig

class ServiceRequestsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.service_requests'

    def ready(self):
        import apps.service_requests.signals