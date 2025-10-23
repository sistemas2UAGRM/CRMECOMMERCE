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
    - MAILCHIMP_API_KEY
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
    MANDRILL_API_KEY = getattr(settings, 'MAILGUN_API_KEY', None)
    FROM_EMAIL = getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@tu-dominio.com')
    FROM_NAME = getattr(settings, 'DEFAULT_FROM_NAME', 'Tu Tienda')

    if not MAILGUN_API_KEY:
        # Si no está Mailgun configurado, intentar enviar con Django (fallback)
        from django.core.mail import EmailMultiAlternatives
        msg = EmailMultiAlternatives(subject, text_body, FROM_EMAIL, [user.email])
        msg.attach_alternative(html_body, "text/html")
        msg.send(fail_silently=True)
        return {'status': 'sent_via_django'}

    # Construir el payload JSON que Mandrill espera
    payload = {
        'key': MANDRILL_API_KEY,
        'message': {
            'html': html_body,
            'text': text_body,
            'subject': subject,
            'from_email': FROM_EMAIL,
            'from_name': FROM_NAME,
            'to': [
                {
                    'email': user.email,
                    'name': user.get_full_name() or user.username,
                    'type': 'to'
                }
            ],
            'important': False,
            'track_opens': True,
            'track_clicks': True,
        },
        'async': False # Lo ponemos síncrono para que la tarea Celery sepa si falló
    }

    try:
        response = requests.post(
            'https://mandrillapp.com/api/1.0/messages/send.json',
            json=payload, # <--- Usamos 'json' en lugar de 'data'
            timeout=10
        )
        response.raise_for_status()
        
        # Mandrill devuelve una lista, comprobamos el estado del primer (y único) email
        result = response.json()
        if result[0]['status'] in ['sent', 'queued']:
            return {'status': result[0]['status'], 'provider': 'mandrill'}
        else:
            # Si Mandrill lo rechazó (ej. 'rejected')
            raise requests.RequestException(f"Mandrill rejected email: {result[0]['reject_reason']}")

    except requests.RequestException as exc:
        # Reintentar con backoff
        try:
            self.retry(exc=exc)
        except Exception:
            return {'status': 'error', 'detail': str(exc)}
