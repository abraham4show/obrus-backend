# Obrus Django Backend

A complete Django REST API backend for the Obrus service requests and job applications platform.

## Features

- **Authentication**: JWT-based authentication with refresh tokens
- **Service Requests**: Multi-step form handling with dynamic JSON fields
- **Job Applications**: File uploads (CVs and photos) with validation
- **Admin Dashboard**: Django admin for managing all data
- **Email Notifications**: Automatic emails on form submissions and status updates
- **In-App Notifications**: Real-time notification system for users
- **Role-Based Access**: Separate roles for admin, staff, clients, and applicants

## Tech Stack

- **Django 5.0+**
- **Django REST Framework**
- **PostgreSQL** (via psycopg2)
- **JWT Authentication** (djangorestframework-simplejwt)
- **CORS Headers** for frontend integration
- **API Documentation** (drf-spectacular/Swagger)

## Project Structure

```
django_backend/
├── apps/
│   ├── core/              # Base models (TimeStampedModel)
│   ├── users/             # Custom User model with roles
│   ├── service_requests/  # Service request handling
│   ├── job_applications/  # Job application handling
│   └── notifications/     # In-app notifications
├── config/                # Django settings
├── media/                 # File uploads (CVs, photos)
├── templates/             # Email templates
├── requirements.txt
├── manage.py
└── .env.example
```

## Quick Start

### 1. Install Dependencies

```bash
cd django_backend
pip install -r requirements.txt
```

### 2. Environment Setup

```bash
cp .env.example .env
# Edit .env with your database and email settings
```

### 3. Database Setup

```bash
# Create PostgreSQL database
createdb obrus_db

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### 4. Run Development Server

```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Authentication
- `POST /api/auth/login/` - Login (get JWT tokens)
- `POST /api/auth/refresh/` - Refresh access token
- `POST /api/auth/register/` - Register new user
- `POST /api/auth/logout/` - Logout (blacklist token)
- `GET /api/auth/profile/` - Get/update profile

### Service Requests
- `GET /api/service-requests/` - List all (admin only)
- `POST /api/service-requests/` - Create new (public)
- `GET /api/service-requests/my-requests/` - My requests
- `GET /api/service-requests/stats/` - Statistics (admin)
- `GET /api/service-requests/<uuid>/` - Get details
- `PUT/PATCH /api/service-requests/<uuid>/` - Update (admin)

### Job Applications
- `GET /api/job-applications/` - List all (admin only)
- `POST /api/job-applications/` - Create new (public)
- `GET /api/job-applications/my-applications/` - My applications
- `GET /api/job-applications/stats/` - Statistics (admin)
- `GET /api/job-applications/<uuid>/` - Get details
- `PUT/PATCH /api/job-applications/<uuid>/` - Update (admin)

### Notifications
- `GET /api/notifications/` - List my notifications
- `GET /api/notifications/unread/` - Unread notifications
- `POST /api/notifications/mark-all-read/` - Mark all read
- `GET /api/notifications/stats/` - Notification stats

### API Documentation
- `GET /api/schema/` - OpenAPI schema
- `GET /api/docs/` - Swagger UI

## Frontend Integration

Your React frontend (Lovable) should connect to these endpoints:

### Environment Variables (Frontend)
```env
VITE_API_BASE_URL=http://localhost:8000/api
```

### Example: Creating a Service Request

```javascript
const createServiceRequest = async (data) => {
  const response = await fetch('http://localhost:8000/api/service-requests/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      full_name: data.fullName,
      company_name: data.companyName,
      phone: data.phone,
      email: data.email,
      location: data.location,
      service_type: data.serviceType, // 'manpower', 'facility', 'environmental', 'equipment'
      service_details: data.serviceDetails // JSON object with dynamic fields
    }),
  });
  return response.json();
};
```

### Example: Uploading Job Application with Files

```javascript
const submitJobApplication = async (formData) => {
  const data = new FormData();
  data.append('full_name', formData.fullName);
  data.append('phone', formData.phone);
  data.append('email', formData.email);
  data.append('position', formData.position);
  data.append('cv', formData.cvFile); // File object
  data.append('photo', formData.photoFile); // File object (optional)

  const response = await fetch('http://localhost:8000/api/job-applications/', {
    method: 'POST',
    body: data, // No Content-Type header needed for FormData
  });
  return response.json();
};
```

### Example: Authenticated Requests

```javascript
const getMyRequests = async (accessToken) => {
  const response = await fetch('http://localhost:8000/api/service-requests/my-requests/', {
    headers: {
      'Authorization': `Bearer ${accessToken}`,
    },
  });
  return response.json();
};
```

## Database Schema

### ServiceRequest
- `id` (UUID, PK)
- `full_name` (string)
- `company_name` (string, optional)
- `phone` (string)
- `email` (string)
- `location` (text)
- `service_type` (enum: manpower/facility/environmental/equipment)
- `service_details` (JSON)
- `status` (enum: pending/in_progress/completed/cancelled)
- `user` (FK to User, optional)
- `admin_notes` (text)
- `created_at`, `updated_at` (timestamps)

### JobApplication
- `id` (UUID, PK)
- `full_name` (string)
- `phone` (string)
- `email` (string)
- `position` (string)
- `cv` (file)
- `photo` (image, optional)
- `status` (enum: received/reviewing/shortlisted/interview/rejected/hired)
- `user` (FK to User, optional)
- `admin_notes` (text)
- `created_at`, `updated_at` (timestamps)

### User (Custom)
- `id` (UUID, PK)
- `email` (unique)
- `username`
- `first_name`, `last_name`
- `phone` (optional)
- `is_client`, `is_applicant`, `is_staff_member` (booleans)
- Separate `UserRole` table for role management

## Email Configuration

The backend sends automatic emails:

1. **Service Request Created**:
   - Admin notification
   - Client confirmation

2. **Service Request Updated**:
   - Client notification when status changes

3. **Job Application Created**:
   - Admin notification
   - Applicant confirmation

4. **Job Application Updated**:
   - Applicant notification when status changes

Configure in `.env`:
```env
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
ADMIN_EMAIL=admin@obrus.com
```

## Deployment

### Using Gunicorn

```bash
pip install gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

### Using Docker

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN python manage.py collectstatic --noinput

CMD gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

### Environment Variables for Production

```env
DEBUG=False
SECRET_KEY=your-production-secret-key
ALLOWED_HOSTS=api.obrus.com,www.api.obrus.com
DATABASE_URL=postgres://user:pass@db:5432/obrus_db
```

## Security Notes

- All API endpoints (except registration and public forms) require authentication
- File uploads are validated (type and size)
- CORS is configured for your frontend domain
- JWT tokens have expiration (1 hour access, 7 days refresh)
- Row-level security: users can only see their own data (except admins)

## Next Steps

1. Set up your PostgreSQL database
2. Configure email settings
3. Run migrations
4. Create a superuser
5. Test the API with the Swagger docs at `/api/docs/`
6. Connect your React frontend to the API endpoints

For questions or issues, check the Django documentation or Django REST Framework documentation.
