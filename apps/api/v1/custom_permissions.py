from rest_framework.permissions import BasePermission

class ProductPermission(BasePermission):
    def has_permission(self, request, view):
        restricted_methods = ['POST', 'PUT', 'DELETE']

        if request.method == 'GET':
            return True
        
        elif request.method in restricted_methods and not request.user.is_staff:
            self.message = f'Only staff members can perform this operation'
            return False
        
        return request.user.is_authenticated