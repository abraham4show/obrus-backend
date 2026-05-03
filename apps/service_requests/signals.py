from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ServiceRequest
from apps.notifications.models import Notification
from apps.users.models import User

@receiver(post_save, sender=ServiceRequest)
def notify_client_on_status_change(sender, instance, created, **kwargs):
    # Notify client on status change (not on creation)
    if not created and instance.user:
        Notification.objects.create(
            user=instance.user,
            notification_type='service_request_updated',
            title="Service Request Status Updated",
            message=f"Your {instance.get_service_type_display()} request is now: {instance.get_status_display()}",
        )

    # Notify all staff members when a new request is created (assigned_to is null)
    if created:
        staff_users = User.objects.filter(roles__role='staff')
        for staff in staff_users:
            Notification.objects.create(
                user=staff,
                notification_type='general',  # or add 'new_service_request' to NOTIFICATION_TYPES
                title="New Service Request",
                message=f"A new {instance.get_service_type_display()} request from {instance.full_name} needs assignment.",
            )