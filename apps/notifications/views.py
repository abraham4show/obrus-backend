from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Count
from .models import Notification
from .serializers import NotificationSerializer, NotificationUpdateSerializer
from .utils import mark_all_as_read


class NotificationListView(generics.ListAPIView):
    """List notifications for the authenticated user."""
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

class MyNotificationsView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')


class NotificationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update (mark as read), or delete a notification."""
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'pk'

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return NotificationUpdateSerializer
        return NotificationSerializer


class UnreadNotificationsView(generics.ListAPIView):
    """List unread notifications for the authenticated user."""
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user, is_read=False)


class MarkAllAsReadView(APIView):
    """Mark all notifications as read."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        mark_all_as_read(request.user)
        return Response({"message": "All notifications marked as read"}, status=status.HTTP_200_OK)


class NotificationStatsView(APIView):
    """Get notification statistics for the authenticated user."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        stats = {
            'total': Notification.objects.filter(user=request.user).count(),
            'unread': Notification.objects.filter(user=request.user, is_read=False).count(),
            'read': Notification.objects.filter(user=request.user, is_read=True).count(),
            'by_type': dict(Notification.objects.filter(user=request.user).values('notification_type').annotate(count=Count('notification_type')).values_list('notification_type', 'count'))
        }
        return Response(stats)
