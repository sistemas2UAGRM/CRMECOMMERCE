# apps/users/tasks.py
"""
Tareas asíncronas relacionadas con usuarios.
Ejemplo: enviar email de verificación usando Mailgun (HTTP API).
"""

import os
import uuid
import requests
from django.conf import settings
from django.template.loader import render_to_string
from django.urls import reverse

from celery import shared_task
from django.contrib.auth import get_user_model

User = get_user_model()

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_verification_email_task(self, user_id):
    """
    Tarea Celery para enviar email de verificación.
    Requiere en settings:
    - MAILGUN_API_KEY
    - MAILGUN_DOMAIN
    - DEFAULT_FROM_EMAIL
    - SITE_URL (ej: https://mi-dominio.com)
    """

    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return {'status': 'error', 'reason': 'user_not_found'}

    # Construir URL de verificación
    token = str(user.verification_uuid)
    site = getattr(settings, 'SITE_URL', 'http://localhost:8000')
    verify_path = reverse('users-verify-email')  # Asegúrate que la url name esté registrada
    verify_url = f"{site}{verify_path}?token={token}"

    # Renderizar templates HTML y texto plano (crea estos templates)
    subject = "Verifica tu email"
    text_body = render_to_string('emails/verify_email.txt', {'user': user, 'verify_url': verify_url})
    html_body = render_to_string('emails/verify_email.html', {'user': user, 'verify_url': verify_url})

    # Preferimos usar Mailgun HTTP API
    MAILGUN_API_KEY = getattr(settings, 'MAILGUN_API_KEY', None)
    MAILGUN_DOMAIN = getattr(settings, 'MAILGUN_DOMAIN', None)
    FROM = getattr(settings, 'DEFAULT_FROM_EMAIL', f"no-reply@{MAILGUN_DOMAIN or 'localhost'}")

    if not MAILGUN_API_KEY or not MAILGUN_DOMAIN:
        # Si no está Mailgun configurado, intentar enviar con Django (fallback)
        from django.core.mail import EmailMultiAlternatives
        msg = EmailMultiAlternatives(subject, text_body, FROM, [user.email])
        msg.attach_alternative(html_body, "text/html")
        msg.send(fail_silently=True)
        return {'status': 'sent_via_django'}

    try:
        response = requests.post(
            f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages",
            auth=("api", MAILGUN_API_KEY),
            data={
                "from": FROM,
                "to": [user.email],
                "subject": subject,
                "text": text_body,
                "html": html_body
            },
            timeout=10
        )
        response.raise_for_status()
        return {'status': 'sent', 'provider': 'mailgun', 'code': response.status_code}
    except requests.RequestException as exc:
        # Reintentar con backoff
        try:
            self.retry(exc=exc)
        except Exception:
            return {'status': 'error', 'detail': str(exc)}
