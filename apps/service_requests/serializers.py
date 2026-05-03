from rest_framework import serializers
from .models import ServiceRequest
from apps.job_applications.models import JobApplication  # Use correct model name

class ServiceRequestSerializer(serializers.ModelSerializer):
    service_type_display = serializers.CharField(source='get_service_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = ServiceRequest
        fields = [
            'id', 'full_name', 'company_name', 'phone', 'email', 'location',
            'service_type', 'service_type_display', 'service_details',
            'status', 'status_display', 'user', 'admin_notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'user']


class ServiceRequestCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceRequest
        fields = [
            'full_name', 'company_name', 'phone', 'email', 'location',
            'service_type', 'service_details'
        ]

    def create(self, validated_data):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['user'] = request.user
        return super().create(validated_data)


class ServiceRequestUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceRequest
        fields = ['status', 'admin_notes', 'assigned_to']   # add assigned_to


class ServiceRequestListSerializer(serializers.ModelSerializer):
    service_type_display = serializers.CharField(source='get_service_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = ServiceRequest
        fields = [
            'id', 'full_name', 'company_name', 'service_type',
            'service_type_display', 'status', 'status_display', 'created_at'
        ]


class JobApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobApplication
        fields = '__all__'