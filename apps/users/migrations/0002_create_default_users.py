from django.db import migrations
from django.contrib.auth.hashers import make_password

def create_users(apps, schema_editor):
    User = apps.get_model('users', 'User')
    UserRole = apps.get_model('users', 'UserRole')
    
    # Create client
    client, created = User.objects.get_or_create(
        email='client@example.com',
        defaults={
            'username': 'client',
            'first_name': 'Client',
            'last_name': 'User',
            'is_client': True,
            'is_staff_member': False,
            'is_staff': False,
            'is_superuser': False,
            'password': make_password('Client123!'),
        }
    )
    if created:
        UserRole.objects.get_or_create(user=client, role='client')
    
    # Create staff
    staff, created = User.objects.get_or_create(
        email='staff@example.com',
        defaults={
            'username': 'staff',
            'first_name': 'Staff',
            'last_name': 'User',
            'is_staff_member': True,
            'is_client': False,
            'is_staff': False,
            'is_superuser': False,
            'password': make_password('Staff123!'),
        }
    )
    if created:
        UserRole.objects.get_or_create(user=staff, role='staff')

def reverse_func(apps, schema_editor):
    User = apps.get_model('users', 'User')
    User.objects.filter(email__in=['client@example.com', 'staff@example.com']).delete()

class Migration(migrations.Migration):
    dependencies = [
        ('users', '0001_initial'),  # adjust to the last migration in your users app
    ]
    operations = [
        migrations.RunPython(create_users, reverse_func),
    ]