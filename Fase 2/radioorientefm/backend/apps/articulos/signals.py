from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from .models import Articulo
from apps.contact.models import Suscripcion


@receiver(post_save, sender=Articulo)
def enviar_newsletter_articulo(sender, instance, created, **kwargs):
    """
    Envía un email HTML a todos los suscriptores activos cuando se publica un nuevo artículo.
    Solo se envía si el artículo es nuevo Y está publicado.
    """
    # Solo enviar si:
    # 1. Es un artículo nuevo (created=True)
    # 2. El artículo está publicado (publicado=True)
    if not created or not instance.publicado:
        return

    # Obtener todos los suscriptores activos
    suscriptores = Suscripcion.objects.filter(activa=True)

    if not suscriptores.exists():
        print("No hay suscriptores activos para enviar el newsletter")
        return

    # Preparar el asunto
    subject = f'📰 Nuevo artículo: {instance.titulo}'
    from_email = settings.DEFAULT_FROM_EMAIL

    # Contador de emails enviados
    sent_count = 0

    for suscripcion in suscriptores:
        try:
            # Preparar URL completa de la imagen
            imagen_url = None
            if instance.imagen_destacada:
                # Si la imagen ya es una URL completa, usarla directamente
                if instance.imagen_destacada.startswith('http'):
                    imagen_url = instance.imagen_destacada
                else:
                    # Si es relativa, agregar el backend_url (donde están los archivos media)
                    backend_url = getattr(settings, 'BACKEND_URL', 'http://localhost:8000')
                    imagen_url = f"{backend_url}{instance.imagen_destacada}"

            # Preparar el contexto para cada suscriptor
            context = {
                'articulo': instance,
                'imagen_articulo': imagen_url,  # URL completa de la imagen
                'site_url': settings.FRONTEND_URL or 'http://localhost:3000',
                'radio_name': 'Radio Oriente',
                'nombre': suscripcion.nombre,
                'suscripcion_token': suscripcion.token_unsuscribe,
            }

            # Renderizar el template HTML
            html_message = render_to_string('emails/nuevo_articulo.html', context)
            plain_message = strip_tags(html_message)  # Versión texto plano como fallback

            # Crear email con soporte HTML
            email = EmailMultiAlternatives(
                subject=subject,
                body=plain_message,  # Versión texto plano
                from_email=from_email,
                to=[suscripcion.email]
            )

            # Adjuntar versión HTML
            email.attach_alternative(html_message, "text/html")

            # Agregar headers para el botón de desuscripción de Gmail
            backend_url = getattr(settings, 'BACKEND_URL', 'http://localhost:8000')
            unsubscribe_url = f"{backend_url}/api/contact/unsubscribe-token/?token={suscripcion.token_unsuscribe}"
            email.extra_headers = {
                'List-Unsubscribe': f'<{unsubscribe_url}>',
                'List-Unsubscribe-Post': 'List-Unsubscribe=One-Click'
            }

            # Enviar
            email.send()
            sent_count += 1

        except Exception as e:
            print(f"Error al enviar email a {suscripcion.email}: {str(e)}")
            continue

    print(f"Newsletter enviado a {sent_count}/{suscriptores.count()} suscriptores para el artículo: {instance.titulo}")
