from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from .models import Suscripcion


@receiver(post_save, sender=Suscripcion)
def enviar_email_bienvenida(sender, instance, created, **kwargs):
    """envía un email de bienvenida cuando se crea una nueva suscripcion. solo se envía si es una suscripcion nueva y está activa"""
    #solo enviar si
    #1. es una suscripcion nueva (created=true)
    #2. la suscripcion está activa (activa=true)
    if not created or not instance.activa:
        return

    try:
        #preparar el contexto para el email
        context = {
            'site_url': settings.FRONTEND_URL or 'http://localhost:3000',
            'radio_name': 'Radio Oriente',
            'nombre': instance.nombre,
        }

        #renderizar el template html
        html_message = render_to_string('emails/bienvenida_suscripcion.html', context)
  #versión texto plano como fallback

        #preparar el asunto
        subject = f'¡Bienvenido a Radio Oriente! 🎉'
        from_email = settings.DEFAULT_FROM_EMAIL

        #crear email con soporte html
        email = EmailMultiAlternatives(
            subject=subject,
  #versión texto plano
            from_email=from_email,
            to=[instance.email]
        )

        #adjuntar versión html
        email.attach_alternative(html_message, "text/html")

        #agregar headers para el botón de desuscripcion de gmail
        backend_url = getattr(settings, 'BACKEND_URL', 'http://localhost:8000')
        unsubscribe_url = f"{backend_url}/api/contact/unsubscribe-token/?token={instance.token_unsuscribe}"
        email.extra_headers = {
            'List-Unsubscribe': f'<{unsubscribe_url}>',
            'List-Unsubscribe-Post': 'List-Unsubscribe=One-Click'
        }

        #enviar
        email.send()

        print(f"Email de bienvenida enviado a: {instance.email}")

    except Exception as e:
        print(f"Error al enviar email de bienvenida a {instance.email}: {str(e)}")
