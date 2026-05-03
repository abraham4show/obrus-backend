# Frontend Integration Guide

## Base URL Configuration

Set your API base URL in your React app:

```env
# .env.development
VITE_API_URL=http://localhost:8000/api

# .env.production
VITE_API_URL=https://your-api-domain.com/api
```

## API Client Setup

Create an API client using fetch or axios:

```typescript
// api/client.ts
const API_BASE_URL = import.meta.env.VITE_API_URL;

export const apiClient = {
  async request(endpoint: string, options: RequestInit = {}) {
    const url = `${API_BASE_URL}${endpoint}`;

    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    // Add auth token if available
    const token = localStorage.getItem('access_token');
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`);
    }

    return response.json();
  },

  get(endpoint: string) {
    return this.request(endpoint, { method: 'GET' });
  },

  post(endpoint: string, data: any) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  patch(endpoint: string, data: any) {
    return this.request(endpoint, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  },

  delete(endpoint: string) {
    return this.request(endpoint, { method: 'DELETE' });
  },
};
```

## Authentication Flow

```typescript
// hooks/useAuth.ts
import { useState, useEffect } from 'react';

export const useAuth = () => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      fetchUser();
    } else {
      setLoading(false);
    }
  }, []);

  const fetchUser = async () => {
    try {
      const response = await apiClient.get('/auth/profile/');
      setUser(response);
    } catch (error) {
      logout();
    } finally {
      setLoading(false);
    }
  };

  const login = async (email: string, password: string) => {
    const response = await apiClient.post('/auth/login/', { email, password });
    localStorage.setItem('access_token', response.access);
    localStorage.setItem('refresh_token', response.refresh);
    setUser(response.user);
    return response.user;
  };

  const register = async (userData: any) => {
    const response = await apiClient.post('/auth/register/', userData);
    localStorage.setItem('access_token', response.access);
    localStorage.setItem('refresh_token', response.refresh);
    setUser(response.user);
    return response.user;
  };

  const logout = async () => {
    const refreshToken = localStorage.getItem('refresh_token');
    if (refreshToken) {
      await apiClient.post('/auth/logout/', { refresh: refreshToken });
    }
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setUser(null);
  };

  return { user, loading, login, register, logout };
};
```

## Service Request Form

```typescript
// components/ServiceRequestForm.tsx
import { useState } from 'react';

export const ServiceRequestForm = () => {
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    fullName: '',
    companyName: '',
    phone: '',
    email: '',
    location: '',
    serviceType: '',
    serviceDetails: {},
  });

  const handleSubmit = async () => {
    const payload = {
      full_name: formData.fullName,
      company_name: formData.companyName,
      phone: formData.phone,
      email: formData.email,
      location: formData.location,
      service_type: formData.serviceType,
      service_details: formData.serviceDetails,
    };

    try {
      const response = await apiClient.post('/service-requests/', payload);
      alert('Service request submitted successfully!');
      // Reset form or redirect
    } catch (error) {
      alert('Error submitting request: ' + error.message);
    }
  };

  // ... render form steps
};
```

## Job Application Form with File Upload

```typescript
// components/JobApplicationForm.tsx
import { useState } from 'react';

export const JobApplicationForm = () => {
  const [formData, setFormData] = useState({
    fullName: '',
    phone: '',
    email: '',
    position: '',
    cv: null as File | null,
    photo: null as File | null,
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const data = new FormData();
    data.append('full_name', formData.fullName);
    data.append('phone', formData.phone);
    data.append('email', formData.email);
    data.append('position', formData.position);

    if (formData.cv) {
      data.append('cv', formData.cv);
    }
    if (formData.photo) {
      data.append('photo', formData.photo);
    }

    try {
      const response = await fetch(`${API_BASE_URL}/job-applications/`, {
        method: 'POST',
        body: data,
        // Don't set Content-Type header - browser will set it with boundary
      });

      if (!response.ok) throw new Error('Upload failed');

      alert('Application submitted successfully!');
    } catch (error) {
      alert('Error submitting application: ' + error.message);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {/* Form fields */}
      <input
        type="file"
        accept=".pdf,.doc,.docx"
        onChange={(e) => setFormData({ ...formData, cv: e.target.files?.[0] || null })}
        required
      />
      <input
        type="file"
        accept="image/*"
        onChange={(e) => setFormData({ ...formData, photo: e.target.files?.[0] || null })}
      />
      <button type="submit">Submit Application</button>
    </form>
  );
};
```

## Dashboard (Authenticated)

```typescript
// pages/Dashboard.tsx
import { useEffect, useState } from 'react';

export const Dashboard = () => {
  const [requests, setRequests] = useState([]);
  const [notifications, setNotifications] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [requestsData, notificationsData] = await Promise.all([
          apiClient.get('/service-requests/my-requests/'),
          apiClient.get('/notifications/'),
        ]);
        setRequests(requestsData.results || requestsData);
        setNotifications(notificationsData.results || notificationsData);
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      }
    };

    fetchData();
  }, []);

  return (
    <div>
      <h1>My Dashboard</h1>

      <section>
        <h2>My Service Requests</h2>
        {requests.map((request) => (
          <div key={request.id}>
            <p>{request.service_type_display} - {request.status_display}</p>
            <p>Submitted: {new Date(request.created_at).toLocaleDateString()}</p>
          </div>
        ))}
      </section>

      <section>
        <h2>Notifications</h2>
        {notifications.map((notification) => (
          <div key={notification.id} className={notification.is_read ? 'read' : 'unread'}>
            <p>{notification.title}</p>
            <p>{notification.message}</p>
          </div>
        ))}
      </section>
    </div>
  );
};
```

## CORS Configuration

Make sure your Django backend allows requests from your frontend:

```python
# config/settings.py
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",      # React dev server
    "http://localhost:5173",      # Vite dev server
    "https://obrus-apex.lovable.app",  # Your production frontend
]
```

## Error Handling

```typescript
// utils/errorHandler.ts
export const handleApiError = (error: any) => {
  if (error.response?.status === 401) {
    // Token expired or invalid
    localStorage.removeItem('access_token');
    window.location.href = '/login';
  } else if (error.response?.status === 403) {
    alert('You do not have permission to perform this action');
  } else {
    alert(error.message || 'An error occurred');
  }
};
```

## Environment Variables

```typescript
// types/env.d.ts
declare global {
  interface ImportMetaEnv {
    readonly VITE_API_URL: string;
  }
  interface ImportMeta {
    readonly env: ImportMetaEnv;
  }
}

export {};
```

This guide should help you integrate your React frontend with the Django backend seamlessly!
