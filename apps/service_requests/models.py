from django.db import models
from django.conf import settings
from apps.core.models import TimeStampedModel

class ServiceRequest(TimeStampedModel):
    SERVICE_TYPES = [
        ('manpower', 'Manpower'),
        ('facility', 'Facility'),
        ('environmental', 'Environmental'),
        ('equipment', 'Equipment'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPES)
    location = models.CharField(max_length=255)
    service_details = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_notes = models.TextField(blank=True)

    # Optional link to registered user (client)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='service_requests'
    )

    # Assigned to staff member
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_service_requests'
    )

    class Meta:
        db_table = 'service_requests'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.service_type} - {self.full_name} - {self.status}"