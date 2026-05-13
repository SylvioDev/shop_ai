from rest_framework.permissions import BasePermission
from rest_framework.permissions import SAFE_METHODS

class ProductPermission(BasePermission):
    def has_permission(self, request, view):
        if not request.is_staff:
            self.message = 'Only staff members can perform this operation'
            return False

        return request.user and request.user.is_staff
class UserPermission(BasePermission):
    message = 'You are not allowed to perform this operation'

    def has_permission(self, request, view):
        if request.method == 'GET':
            return True
    
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # ONLY owner allowed
        return obj.username == request.user.username
    
class UserProfilePermission(UserPermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
    



        