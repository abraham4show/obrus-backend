from rest_framework import generics, permissions, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.core.mail import send_mail
from django.conf import settings
from apps.job_applications.models import JobApplication
from .serializers import (
    JobApplicationSerializer,
    JobApplicationCreateSerializer,
    JobApplicationUpdateSerializer,
    JobApplicationListSerializer
)
from apps.notifications.utils import send_notification
from apps.users.models import User
from rest_framework.permissions import IsAuthenticated


class IsAdminOrStaff(permissions.BasePermission):
    """Custom permission to only allow admins or staff."""
    def has_permission(self, request, view):
        return request.user and (request.user.is_staff or request.user.is_superuser)


class JobApplicationListCreateView(generics.ListCreateAPIView):
    """
    GET: List all job applications (admin/staff only)
    POST: Create new job application (public or authenticated)
    """
    queryset = JobApplication.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'position', 'created_at']
    search_fields = ['full_name', 'email', 'phone', 'position']
    ordering_fields = ['created_at', 'status']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return JobApplicationCreateSerializer
        return JobApplicationListSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.AllowAny()]
        return [IsAdminOrStaff()]

    def perform_create(self, serializer):
        instance = serializer.save()

        # Send email notification to admin
        admin_message = f"""A new job application has been submitted:

Name: {instance.full_name}
Email: {instance.email}
Phone: {instance.phone}
Position: {instance.position}

CV: {instance.cv.url if instance.cv else 'No CV attached'}
Photo: {'Attached' if instance.photo else 'No photo attached'}

View in admin: {settings.ALLOWED_HOSTS[0]}/admin/
"""

        send_mail(
            subject=f'New Job Application: {instance.position}',
            message=admin_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.ADMIN_EMAIL],
            fail_silently=True,
        )

        # Send confirmation email to applicant
        applicant_message = f"""Dear {instance.full_name},

Thank you for applying for the {instance.position} position at Obrus.

We have received your application and our HR team will review it shortly. You will receive an update on your application status soon.

Application ID: {instance.id}
Position: {instance.position}
Status: {instance.get_status_display()}

Best regards,
Obrus HR Team
"""

        send_mail(
            subject='We received your job application',
            message=applicant_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[instance.email],
            fail_silently=True,
        )

        # Create in-app notification
        if instance.user:
            send_notification(
                user=instance.user,
                notification_type='job_application_created',
                title='Application Received',
                message=f'Your application for {instance.position} has been received.',
                related_object=instance
            )


class JobApplicationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a job application.
    - Admin/Staff: Full access
    - Owner (if authenticated): Read-only
    """
    queryset = JobApplication.objects.all()
    serializer_class = JobApplicationSerializer
    lookup_field = 'pk'

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAdminOrStaff()]
        return [permissions.IsAuthenticated()]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return JobApplicationUpdateSerializer
        return JobApplicationSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return JobApplication.objects.all()
        return JobApplication.objects.filter(user=user)

    def perform_update(self, serializer):
        instance = serializer.save()

        # Send notification if status changed
        if 'status' in self.request.data:
            # Email to applicant
            status_message = f"""Dear {instance.full_name},

Your job application status has been updated to: {instance.get_status_display()}

Application ID: {instance.id}
Position: {instance.position}

{instance.admin_notes if instance.admin_notes else ''}

Best regards,
Obrus HR Team
"""

            send_mail(
                subject='Update on your job application',
                message=status_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[instance.email],
                fail_silently=True,
            )

            # In-app notification
            if instance.user:
                send_notification(
                    user=instance.user,
                    notification_type='job_application_updated',
                    title='Application Status Updated',
                    message=f'Your application is now: {instance.get_status_display()}',
                    related_object=instance
                )


class MyJobApplicationsView(generics.ListAPIView):
    serializer_class = JobApplicationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return JobApplication.objects.filter(user=self.request.user)


class JobApplicationStatsView(APIView):
    """Get job application statistics (admin only)."""
    permission_classes = [IsAdminOrStaff]

    def get(self, request):
        from django.db.models import Count

        stats = {
            'total': JobApplication.objects.count(),
            'by_status': dict(JobApplication.objects.values('status').annotate(count=Count('status')).values_list('status', 'count')),
            'by_position': dict(JobApplication.objects.values('position').annotate(count=Count('position')).values_list('position', 'count')),
            'received': JobApplication.objects.filter(status='received').count(),
            'reviewing': JobApplication.objects.filter(status='reviewing').count(),
            'shortlisted': JobApplication.objects.filter(status='shortlisted').count(),
        }
        return Response(stats)
