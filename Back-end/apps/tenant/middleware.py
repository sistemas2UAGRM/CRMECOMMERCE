from django.http import HttpResponseForbidden
from .models import Tenant

class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        domain = request.get_host().split(':')[0]
        try:
            tenant = Tenant.objects.get(domain=domain)
            request.tenant = tenant
        except Tenant.DoesNotExist:
            return HttpResponseForbidden('Tenant not found')

        response = self.get_response(request)
        return response