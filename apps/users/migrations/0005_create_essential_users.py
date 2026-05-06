from django.db import migrations

def ensure_roles(apps, schema_editor):
    User = apps.get_model('users', 'User')
    UserRole = apps.get_model('users', 'UserRole')
    
    # Admin
    admin = User.objects.filter(email='admin@example.com').first()
    if admin:
        UserRole.objects.get_or_create(user=admin, role='admin')
        # Ensure admin has staff/superuser flags
        if not admin.is_staff:
            admin.is_staff = True
        if not admin.is_superuser:
            admin.is_superuser = True
        admin.save()
    else:
        # If admin doesn't exist, create it (but it should exist via superuser creation)
        admin = User.objects.create_superuser(
            email='admin@example.com',
            password='Admin123!',
            first_name='Admin',
            last_name='User',
            username='admin'
        )
        UserRole.objects.create(user=admin, role='admin')
    
    # Client
    client = User.objects.filter(email='client@example.com').first()
    if not client:
        client = User.objects.create_user(
            email='client@example.com',
            password='Client123!',
            first_name='Client',
            last_name='User',
            username='client',
            is_client=True
        )
    UserRole.objects.get_or_create(user=client, role='client')
    
    # Staff
    staff = User.objects.filter(email='staff@example.com').first()
    if not staff:
        staff = User.objects.create_user(
            email='staff@example.com',
            password='Staff123!',
            first_name='Staff',
            last_name='User',
            username='staff',
            is_staff_member=True
        )
    UserRole.objects.get_or_create(user=staff, role='staff')

def reverse_func(apps, schema_editor):
    User = apps.get_model('users', 'User')
    UserRole = apps.get_model('users', 'UserRole')
    UserRole.objects.filter(role__in=['admin', 'client', 'staff']).delete()
    User.objects.filter(email__in=['admin@example.com', 'client@example.com', 'staff@example.com']).delete()

class Migration(migrations.Migration):
    dependencies = [
        ('users', '0004_add_admin_role'),  # replace with your last users migration number
    ]
    operations = [
        migrations.RunPython(ensure_roles, reverse_func),
    ]