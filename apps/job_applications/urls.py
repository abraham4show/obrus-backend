from django.urls import path
from .views import (
    JobApplicationListCreateView,
    JobApplicationDetailView,
    MyJobApplicationsView,
    JobApplicationStatsView
)
from apps.service_requests.views import admin_stats  # only this one exists

urlpatterns = [
    path('', JobApplicationListCreateView.as_view(), name='job-application-list'),
    path('my-applications/', MyJobApplicationsView.as_view(), name='my-job-applications'),
    path('stats/', JobApplicationStatsView.as_view(), name='job-application-stats'),
    path('<int:pk>/', JobApplicationDetailView.as_view(), name='job-application-detail'),
    path('api/admin/stats/', admin_stats, name='admin_stats'),
    # Comment out the other admin endpoints until they are implemented
    # path('api/admin/requests/', admin_requests, name='admin_requests'),
    # path('api/admin/staff-list/', admin_staff_list, name='admin_staff_list'),
    # path('api/admin/staff-applications/', admin_staff_applications, name='admin_staff_applications'),
    # path('api/admin/staff-approve/<int:user_id>/', admin_staff_approve, name='admin_staff_approve'),
    # path('api/admin/staff-reject/<int:user_id>/', admin_staff_reject, name='admin_staff_reject'),
    # path('api/admin/broadcast/', admin_broadcast, name='admin_broadcast'),
]