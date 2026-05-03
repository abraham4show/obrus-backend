from django.apps import AppConfig
from django.apps import AppConfig
from django.db.models.signals import post_migrate

class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.users'



def create_default_admin(sender, **kwargs):
    from .models import User, UserRole
    if not User.objects.filter(email='admin@example.com').exists():
        admin = User.objects.create_superuser(
            email='admin@example.com',
            password='Admin123!',
            first_name='Admin',
            last_name='User',
            is_staff=True,
            is_superuser=True
        )
        UserRole.objects.get_or_create(user=admin, role='admin')

class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.users'
    def ready(self):
        post_migrate.connect(create_default_admin, sender=self)