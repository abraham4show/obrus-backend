import logging 
logger = logging.getLogger(__name__)
import socket
socket.setdefaulttimeout(5)  # at the top of views.py
from rest_framework import generics, permissions, filters, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.core.mail import send_mail
from django.conf import settings
from .models import ServiceRequest
from .serializers import (
    ServiceRequestSerializer,
    ServiceRequestCreateSerializer,
    ServiceRequestUpdateSerializer,
    ServiceRequestListSerializer,
    JobApplicationSerializer,
)
from apps.users.models import User
from apps.job_applications.models import JobApplication
from apps.notifications.utils import send_notification
from .permissions import IsAssignedStaffOrAdmin
from rest_framework.decorators import api_view
from django.db.models import Count
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from apps.users.models import UserRole
from apps.notifications.models import Message 
from apps.users.serializers import UserSerializer
from apps.notifications.models import Notification
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import ServiceRequest
from .serializers import ServiceRequestSerializer
from apps.users.models import User
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from apps.users.serializers import serializer


class IsAdminOrStaff(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        # Check if user has admin role
        if request.user.roles.filter(role='admin').exists():
            return True
        # Check if user has staff role
        if request.user.roles.filter(role='staff').exists():
            return True
        return False


class AssignedToMeView(generics.ListAPIView):
    serializer_class = ServiceRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ServiceRequest.objects.filter(assigned_to=self.request.user).order_by('-created_at')


class ServiceRequestListCreateView(generics.ListCreateAPIView):
    queryset = ServiceRequest.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['service_type', 'status', 'created_at']
    search_fields = ['full_name', 'company_name', 'email', 'phone']
    ordering_fields = ['created_at', 'status']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ServiceRequestCreateSerializer
        return ServiceRequestListSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.AllowAny()]
        return [IsAdminOrStaff()]

@method_decorator(csrf_exempt, name='dispatch')
class ServiceRequestDetailView(generics.RetrieveUpdateDestroyAPIView):
    # ...
    queryset = ServiceRequest.objects.all()
    serializer_class = ServiceRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'pk'

def perform_create(self, serializer):
    instance = serializer.save()
    
    # Admin notification
    try:
        admin_message = f"""A new service request has been submitted:

Name: {instance.full_name}
Company: {instance.company_name or 'N/A'}
Email: {instance.email}
Phone: {instance.phone}
Service Type: {instance.get_service_type_display()}
Location: {instance.location}

Details: {instance.service_details}

View in admin: {settings.ALLOWED_HOSTS[0]}/admin/
"""
        send_mail(
            subject=f'New Service Request: {instance.service_type}',
            message=admin_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.ADMIN_EMAIL],
            fail_silently=True,
        )
    except Exception as e:
        logger.error(f"Admin email failed: {e}")

    # Client notification
    try:
        client_message = f"""Dear {instance.full_name},

Thank you for submitting your service request for {instance.get_service_type_display()}.

We have received your request and our team will review it shortly. You will receive an update once we begin processing your request.

Request ID: {instance.id}
Status: {instance.get_status_display()}

Best regards,
Obrus Team
"""
        send_mail(
            subject='We received your service request',
            message=client_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[instance.email],
            fail_silently=True,
        )
    except Exception as e:
        logger.error(f"Client email failed: {e}")

    if instance.user:
        try:
            send_notification(
                user=instance.user,
                notification_type='service_request_created',
                title='Service Request Received',
                message=f'Your {instance.get_service_type_display()} request has been received.',
                related_object=instance
            )
        except Exception as e:
            logger.error(f"Notification failed: {e}")



    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAdminOrStaff()]
        return [permissions.IsAuthenticated()]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ServiceRequestUpdateSerializer
        return ServiceRequestSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser or user.roles.filter(role='staff').exists():
            return ServiceRequest.objects.all()
        return ServiceRequest.objects.filter(user=user)

    def perform_update(self, serializer):
        instance = serializer.save()

        if 'status' in self.request.data:
            status_message = f"""Dear {instance.full_name},

Your service request status has been updated to: {instance.get_status_display()}

Request ID: {instance.id}
Service Type: {instance.get_service_type_display()}

{instance.admin_notes if instance.admin_notes else ''}

Best regards,
Obrus Team
"""
            send_mail(
                subject='Update on your service request',
                message=status_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[instance.email],
                fail_silently=True,
            )

            if instance.user:
                send_notification(
                    user=instance.user,
                    notification_type='service_request_updated',
                    title='Service Request Updated',
                    message=f'Your request status is now: {instance.get_status_display()}',
                    related_object=instance
                )


class MyServiceRequestsView(generics.ListAPIView):
    serializer_class = ServiceRequestListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ServiceRequest.objects.filter(user=self.request.user)


class ServiceRequestStatsView(APIView):
    permission_classes = [IsAdminOrStaff]

    def get(self, request):
        stats = {
            'total': ServiceRequest.objects.count(),
            'by_status': dict(ServiceRequest.objects.values('status').annotate(count=Count('status')).values_list('status', 'count')),
            'by_type': dict(ServiceRequest.objects.values('service_type').annotate(count=Count('service_type')).values_list('service_type', 'count')),
            'pending': ServiceRequest.objects.filter(status='pending').count(),
            'in_progress': ServiceRequest.objects.filter(status='in_progress').count(),
            'completed': ServiceRequest.objects.filter(status='completed').count(),
        }
        return Response(stats)



@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
def admin_stats(request):
    print("=== admin_stats view called ===")  # Add this line
    # Your existing code (with or without internal role checks)
    total_users = User.objects.filter(roles__role='client').count()
    total_requests = ServiceRequest.objects.count()
    total_staff = User.objects.filter(roles__role='staff').count()
    total_jobs = JobApplication.objects.count()
    most_requested = ServiceRequest.objects.values('service_type').annotate(total=Count('service_type')).order_by('-total').first()
    recent_requests = ServiceRequest.objects.all().order_by('-created_at')[:10]
    recent_applications = JobApplication.objects.all().order_by('-created_at')[:10]
    return Response({
        'totalUsers': total_users,
        'totalRequests': total_requests,
        'totalStaff': total_staff,
        'totalJobs': total_jobs,
        'mostRequestedService': most_requested['service_type'] if most_requested else 'N/A',
        'recentRequests': ServiceRequestSerializer(recent_requests, many=True).data,
        'recentApplications': JobApplicationSerializer(recent_applications, many=True).data,
    })


@api_view(['GET'])
def admin_users(request):
    if not request.user.is_authenticated:
        return Response({'error': 'Not authenticated'}, status=401)
    # Fallback: use is_staff or is_superuser if roles not available
    if not (request.user.is_staff or request.user.is_superuser or request.user.roles.filter(role='admin').exists()):
        return Response({'error': 'Admin access required'}, status=403)
    users = User.objects.all().order_by('-date_joined')
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def admin_staff_applications(request):
    # Users with role 'staff' that are not yet approved? Assuming we have is_staff_approved field.
    # If not, we'll just return all staff users.
    if not request.user.is_authenticated or not request.user.roles.filter(role='admin').exists():
        return Response({'error': 'Unauthorized'}, status=401)
    # For simplicity, return all users with role 'staff' (they are already staff)
    # But we need pending applications – you may have a StaffProfile model. Let's assume is_staff_member=False and role='staff' means pending.
    pending = User.objects.filter(roles__role='staff', is_staff_member=False)
    data = [{'id': u.id, 'email': u.email, 'full_name': u.full_name, 'phone': u.phone} for u in pending]
    return Response(data)

@api_view(['GET'])
def admin_jobs(request):
    # If you have a Job model, implement; otherwise return empty list
    # For now, return an empty list to avoid 404
    return Response([])

@api_view(['GET'])
def admin_recruitment(request):
    # This should list job applications (already have stats)
    apps = JobApplication.objects.all().order_by('-created_at')
    serializer = JobApplicationSerializer(apps, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def admin_staff_approve(request, user_id):
    if not request.user.is_authenticated or not request.user.roles.filter(role='admin').exists():
        return Response({'error': 'Unauthorized'}, status=401)
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)
    # Mark as staff member
    user.is_staff_member = True
    user.save()
    # Ensure they have the staff role
    UserRole.objects.get_or_create(user=user, role='staff')
    return Response({'message': 'Staff approved'})

@api_view(['POST'])
def admin_staff_reject(request, user_id):
    if not request.user.is_authenticated or not request.user.roles.filter(role='admin').exists():
        return Response({'error': 'Unauthorized'}, status=401)
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)
    # Remove staff role and mark as not staff member
    user.roles.filter(role='staff').delete()
    user.is_staff_member = False
    user.save()
    # Optionally delete the user? Usually just remove role.
    return Response({'message': 'Staff rejected'})



 # adjust import if Message is elsewhere

@api_view(['POST'])
def admin_broadcast(request):
    if not request.user.is_authenticated or not request.user.roles.filter(role='admin').exists():
        return Response({'error': 'Unauthorized'}, status=401)
    subject = request.data.get('subject')
    body = request.data.get('message')
    if not subject or not body:
        return Response({'error': 'Subject and message required'}, status=400)
    for user in User.objects.all():
        # Save as Message for admin history
        Message.objects.create(
            sender=request.user,
            recipient=user,
            subject=subject,
            body=body,
            is_broadcast=True
        )
        # Also create a Notification for the user (staff dashboard displays notifications)
        Notification.objects.create(
            user=user,
            title=subject,
            message=body,
            notification_type='general',
        )
    return Response({'message': f'Broadcast sent to {User.objects.count()} users'})



@api_view(['POST'])
def admin_notify_staff(request):
    if not request.user.is_authenticated or not request.user.roles.filter(role='admin').exists():
        return Response({'error': 'Unauthorized'}, status=401)
    title = request.data.get('title')
    message_text = request.data.get('message')
    if not title or not message_text:
        return Response({'error': 'Title and message required'}, status=400)
    staff_users = User.objects.filter(roles__role='staff')
    for staff in staff_users:
        Notification.objects.create(
            user=staff,  # use 'user' not 'recipient'
            title=title,
            message=message_text,
            notification_type='general',  # add required field
        )
    return Response({'message': f'Notification sent to {staff_users.count()} staff members'})

@api_view(['GET'])
def admin_requests(request):
    if not request.user.is_authenticated:
        return Response({'error': 'Not authenticated'}, status=401)
    # Check admin via roles or staff/superuser
    if not (request.user.is_staff or request.user.is_superuser or request.user.roles.filter(role='admin').exists()):
        return Response({'error': 'Admin access required'}, status=403)
    requests = ServiceRequest.objects.all().order_by('-created_at')
    serializer = ServiceRequestSerializer(requests, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def admin_staff_list(request):
    if not request.user.is_authenticated:
        return Response({'error': 'Not authenticated'}, status=401)
    if not (request.user.is_staff or request.user.is_superuser or request.user.roles.filter(role='admin').exists()):
        return Response({'error': 'Admin access required'}, status=403)
    staff_users = User.objects.filter(roles__role='staff', is_staff_member=True)
    data = [{'id': str(u.id), 'full_name': u.full_name} for u in staff_users]
    return Response(data)
