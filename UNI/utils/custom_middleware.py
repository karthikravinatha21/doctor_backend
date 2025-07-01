from django.http import JsonResponse
from django.conf import settings

from apps.approles.models import ApiPermission
from utils.constants import custom_json_response


class RoleBasedAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Get the user's role and the endpoint being accessed
        user_role = ""#request.user.role  # Assuming you have user roles defined
        endpoint = request.path
        method = request.method
        skip_endpoints = ['/api/admin/login/']
        if endpoint in skip_endpoints:
            pass
        else:
            # Check if this role is allowed to access the endpoint
            is_allowed = ApiPermission.objects.filter(endpoint=endpoint, method=method, role=user_role, is_active=True).exists()

            if not is_allowed:
                return custom_json_response(message="Access Denied", status=403)

        # Proceed to the next middleware/view
        response = self.get_response(request)
        return response
