from django.contrib.contenttypes.models import ContentType
from .models import Notification


def send_notification(user, notification_type, title, message, related_object=None):
    """
    Create an in-app notification for a user.

    Args:
        user: The user to notify
        notification_type: Type of notification (from NOTIFICATION_TYPES choices)
        title: Notification title
        message: Notification message
        related_object: Optional related object (ServiceRequest or JobApplication)
    """
    if not user:
        return None

    notification_data = {
        'user': user,
        'notification_type': notification_type,
        'title': title,
        'message': message,
    }

    if related_object:
        notification_data['content_type'] = ContentType.objects.get_for_model(related_object)
        notification_data['object_id'] = related_object.id

    return Notification.objects.create(**notification_data)


def mark_notification_as_read(notification_id, user):
    """Mark a notification as read for a specific user."""
    try:
        notification = Notification.objects.get(id=notification_id, user=user)
        notification.is_read = True
        notification.save()
        return True
    except Notification.DoesNotExist:
        return False


def get_unread_count(user):
    """Get count of unread notifications for a user."""
    return Notification.objects.filter(user=user, is_read=False).count()


def mark_all_as_read(user):
    """Mark all notifications as read for a user."""
    Notification.objects.filter(user=user, is_read=False).update(is_read=True)
