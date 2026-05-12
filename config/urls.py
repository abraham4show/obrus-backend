"""
URL configuration for obrus_backend project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

# Import admin views from service_requests
from apps.service_requests.views import (
    admin_broadcast, admin_staff_list, admin_stats, admin_users,admin_requests,
    admin_staff_applications, admin_recruitment,
    admin_staff_approve, admin_staff_reject, admin_notify_staff
)

# Import job API views
from apps.jobs.api import JobListCreateView, JobDetailView
from rest_framework_simplejwt.views import TokenRefreshView
from apps.core.views import GetCSRFTokenView

urlpatterns = [
    # Django admin
    path('admin/', admin.site.urls),

    # API documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    # App includes
    path('api/auth/', include('apps.users.urls')),
    path('api/service-requests/', include('apps.service_requests.urls')),
    path('api/job-applications/', include('apps.job_applications.urls')),
    path('api/notifications/', include('apps.notifications.urls')),
    path('accounts/', include('allauth.urls')),   # <--- ADD THIS LINE

    # Admin endpoints (custom)
    path('api/admin/stats/', admin_stats, name='admin_stats'),
    path('api/admin/broadcast/', admin_broadcast, name='admin_broadcast'),
    path('api/admin/users/', admin_users, name='admin_users'),
    path('api/admin/staff-applications/', admin_staff_applications, name='admin_staff_applications'),
    path('api/admin/recruitment/', admin_recruitment, name='admin_recruitment'),
    path('api/admin/staff-approve/<uuid:user_id>/', admin_staff_approve, name='admin_staff_approve'),
    path('api/admin/staff-reject/<uuid:user_id>/', admin_staff_reject, name='admin_staff_reject'),
    path('api/admin/notify-staff/', admin_notify_staff, name='admin_notify_staff'),

    # Job endpoints (public and admin)
    path('api/jobs/', JobListCreateView.as_view(), name='job-list'),           # GET for all, POST for admin
    path('api/jobs/<uuid:id>/', JobDetailView.as_view(), name='job-detail'),   # GET, PUT, DELETE for admin
    path('api/admin/jobs/', JobListCreateView.as_view(), name='admin-job-list-create'),  # same as above (optional)
    path('api/admin/jobs/<uuid:id>/', JobDetailView.as_view(), name='admin-job-detail'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
path('api/admin/staff-list/', admin_staff_list, name='admin_staff_list'),
path('api/admin/requests/', admin_requests, name='admin_requests'),
    path('api/get-csrf-token/', GetCSRFTokenView.as_view(), name='get-csrf-token'),
    ]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)