from django.db import models
from django.conf import settings
from apps.jobs.models import Job

class JobApplication(models.Model):
    STATUS_CHOICES = [
        ('received', 'Received'),
        ('reviewing', 'Reviewing'),
        ('shortlisted', 'Shortlisted'),
        ('interview', 'Interview'),
        ('rejected', 'Rejected'),
        ('hired', 'Hired'),
    ]

    # Job relation
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications', null=True, blank=True)

    # Personal Information
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    cover_letter = models.TextField(blank=True, null=True)
    # Position (deprecated? you might remove if job is used)
    position = models.CharField(max_length=255)

    # Files
    cv = models.FileField(upload_to='cvs/%Y/%m/')
    photo = models.ImageField(upload_to='photos/%Y/%m/', blank=True, null=True)

    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='received')

    # Optional link to registered user
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='job_applications')

    # Admin notes
    admin_notes = models.TextField(blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'job_applications'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.full_name} - {self.position} - {self.status}"

    @property
    def cv_filename(self):
        return self.cv.name.split('/')[-1] if self.cv else None

    @property
    def photo_filename(self):
        return self.photo.name.split('/')[-1] if self.photo else None