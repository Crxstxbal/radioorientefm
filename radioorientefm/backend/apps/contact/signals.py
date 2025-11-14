from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from .models import Suscripcion


@receiver(post_save, sender=Suscripcion)
def enviar_email_bienvenida(sender, instance, created, **kwargs):
    """
    Envía un email de bienvenida cuando se crea una nueva suscripción.
    Solo se envía si es una suscripción nueva Y está activa.
    """
    # Solo enviar si:
    # 1. Es una suscripción nueva (created=True)
    # 2. La suscripción está activa (activa=True)
    if not created or not instance.activa:
        return

    try:
        # Preparar el contexto para el email
        context = {
            'site_url': settings.FRONTEND_URL or 'http://localhost:3000',
            'radio_name': 'Radio Oriente',
            'nombre': instance.nombre,
        }

        # Renderizar el template HTML
        html_message = render_to_string('emails/bienvenida_suscripcion.html', context)
        plain_message = strip_tags(html_message)  # Versión texto plano como fallback

        # Preparar el asunto
        subject = f'¡Bienvenido a Radio Oriente! 🎉'
        from_email = settings.DEFAULT_FROM_EMAIL

        # Crear email con soporte HTML
        email = EmailMultiAlternatives(
            subject=subject,
            body=plain_message,  # Versión texto plano
            from_email=from_email,
            to=[instance.email]
        )

        # Adjuntar versión HTML
        email.attach_alternative(html_message, "text/html")

        # Agregar headers para el botón de desuscripción de Gmail
        backend_url = getattr(settings, 'BACKEND_URL', 'http://localhost:8000')
        unsubscribe_url = f"{backend_url}/api/contact/unsubscribe-token/?token={instance.token_unsuscribe}"
        email.extra_headers = {
            'List-Unsubscribe': f'<{unsubscribe_url}>',
            'List-Unsubscribe-Post': 'List-Unsubscribe=One-Click'
        }

        # Enviar
        email.send()

        print(f"Email de bienvenida enviado a: {instance.email}")

    except Exception as e:
        print(f"Error al enviar email de bienvenida a {instance.email}: {str(e)}")
