from django.urls import path
from .views import (
    MyNotificationsView,
    NotificationListView,
    NotificationDetailView,
    UnreadNotificationsView,
    MarkAllAsReadView,
    NotificationStatsView
)

urlpatterns = [
    path('', NotificationListView.as_view(), name='notification-list'),
    path('unread/', UnreadNotificationsView.as_view(), name='unread-notifications'),
    path('mark-all-read/', MarkAllAsReadView.as_view(), name='mark-all-read'),
    path('stats/', NotificationStatsView.as_view(), name='notification-stats'),
    path('<uuid:pk>/', NotificationDetailView.as_view(), name='notification-detail'),
    path('my-notifications/', MyNotificationsView.as_view())
]
