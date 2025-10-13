from ipaddress import ip_address
from django.dispatch import receiver
from .signals import action_log
from .models import Bitacora

@receiver(action_log)
def set_action_log(sender, user, action='login', request=None, **kwargs):
    Bitacora.objects.create(
        user=user,
        action=action,
        tenant=request.tenant,
        ip_address = get_client_ip(request)
    )

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')
