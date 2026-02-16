from rest_framework import permissions

class IsCompany(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'COMPANY'

class IsFreelancerOrExpert(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['FREELANCER', 'EXPERT']

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        # Jobs are owned by company users
        if hasattr(obj, 'company'):
            return obj.company == request.user
        # Proposals are owned by freelancer/expert users
        if hasattr(obj, 'applicant'):
            return obj.applicant == request.user
        return False
