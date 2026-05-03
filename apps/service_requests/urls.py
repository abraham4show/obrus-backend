from django.urls import path
from .views import (
    AssignedToMeView,
    ServiceRequestListCreateView,
    ServiceRequestDetailView,
    MyServiceRequestsView,
    ServiceRequestStatsView
)

from apps.service_requests.views import admin_stats, admin_users, admin_staff_applications, admin_staff_approve, admin_staff_reject

urlpatterns = [
    path('', ServiceRequestListCreateView.as_view(), name='service-request-list'),
    path('my-requests/', MyServiceRequestsView.as_view(), name='my-service-requests'),
    path('stats/', ServiceRequestStatsView.as_view(), name='service-request-stats'),
    path('<uuid:pk>/', ServiceRequestDetailView.as_view(), name='service-request-detail'),
    path('assigned-to-me/', AssignedToMeView.as_view(), name='assigned-to-me'),
    path('api/admin/stats/', admin_stats, name='admin_stats'),
    path('api/admin/users/', admin_users, name='admin_users'),
    path('api/admin/staff-applications/', admin_staff_applications, name='admin_staff_applications'),
    path('api/admin/staff-approve/<int:user_id>/', admin_staff_approve, name='admin_staff_approve'),
    path('api/admin/staff-reject/<int:user_id>/', admin_staff_reject, name='admin_staff_reject'),
    # path('<uuid:pk>/', ServiceRequestDetailView.as_view(), name='service-request-detail'),
]


