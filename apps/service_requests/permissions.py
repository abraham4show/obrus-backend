from rest_framework import permissions

class IsAssignedStaffOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        print(f"Checking: user={request.user}, is_staff={request.user.is_staff}, is_superuser={request.user.is_superuser}")
        print(f"Roles: {[r.role for r in request.user.roles.all()]}")
        if request.user.is_staff or request.user.is_superuser:
            print("Admin access granted")
            return True
        if obj.assigned_to == request.user:
            print("Assigned staff access granted")
            return True
        print("Access denied")
        return False