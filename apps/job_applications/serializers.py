from rest_framework import serializers
from .models import JobApplication

class JobApplicationSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    cv_url = serializers.SerializerMethodField()
    photo_url = serializers.SerializerMethodField()
    cv_filename = serializers.CharField(read_only=True)
    photo_filename = serializers.CharField(read_only=True)
    cover_letter = serializers.CharField(read_only=True)   # read-only, will be set during create

    class Meta:
        model = JobApplication
        fields = [
            'id', 'full_name', 'phone', 'email', 'position',
            'cv', 'cv_url', 'cv_filename', 'photo', 'photo_url', 'photo_filename',
            'status', 'status_display', 'user', 'admin_notes',
            'cover_letter', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'user', 'cover_letter']

    def get_cv_url(self, obj):
        if obj.cv:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.cv.url)
        return None

    def get_photo_url(self, obj):
        if obj.photo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.photo.url)
        return None


class JobApplicationCreateSerializer(serializers.ModelSerializer):
    cover_letter = serializers.CharField(required=False, allow_blank=True, write_only=True)
    class Meta:
        model = JobApplication
        fields = ['full_name', 'phone', 'email', 'position', 'cv', 'photo', 'job', 'cover_letter']

    def validate_cv(self, value):
        if value:
            ext = value.name.split('.')[-1].lower()
            if ext not in ['pdf', 'doc', 'docx']:
                raise serializers.ValidationError('CV must be PDF, DOC, or DOCX format')
            if value.size > 10 * 1024 * 1024:
                raise serializers.ValidationError('CV file size must be under 10MB')
        return value

    def validate_photo(self, value):
        if value:
            ext = value.name.split('.')[-1].lower()
            if ext not in ['jpg', 'jpeg', 'png']:
                raise serializers.ValidationError('Photo must be JPG or PNG format')
            if value.size > 5 * 1024 * 1024:
                raise serializers.ValidationError('Photo file size must be under 5MB')
        return value

    def create(self, validated_data):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['user'] = request.user
        return super().create(validated_data)


class JobApplicationUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobApplication
        fields = ['status', 'admin_notes']


class JobApplicationListSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = JobApplication
        fields = [
            'id', 'full_name', 'position', 'status',
            'status_display', 'created_at'
        ]