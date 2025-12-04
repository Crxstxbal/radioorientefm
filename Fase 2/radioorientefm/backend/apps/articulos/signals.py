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
    """envía un email html a todos los suscriptores activos cuando se publica un nuevo artículo. solo se envía si el artículo es nuevo y está publicado"""
    #solo enviar si
    #1. es un artículo nuevo (created=true)
    #2. el artículo está publicado (publicado=true)
    if not created or not instance.publicado:
        return

    #obtener todos los suscriptores activos
    suscriptores = Suscripcion.objects.filter(activa=True)

    if not suscriptores.exists():
        print("No hay suscriptores activos para enviar el newsletter")
        return

    #preparar el asunto
    subject = f'📰 Nuevo artículo: {instance.titulo}'
    from_email = settings.DEFAULT_FROM_EMAIL

    #contador de emails enviados
    sent_count = 0

    for suscripcion in suscriptores:
        try:
            #preparar url completa de la imagen
            imagen_url = None
            if instance.imagen_destacada:
                #si la imagen ya es una url completa, usarla directamente
                if instance.imagen_destacada.startswith('http'):
                    imagen_url = instance.imagen_destacada
                else:
                    #si es relativa, agregar el backend_url (donde están los archivos media)
                    backend_url = getattr(settings, 'BACKEND_URL', 'http://localhost:8000')
                    imagen_url = f"{backend_url}{instance.imagen_destacada}"

            #preparar el contexto para cada suscriptor
            context = {
                'articulo': instance,
  #url completa de la imagen
                'site_url': settings.FRONTEND_URL or 'http://localhost:3000',
                'radio_name': 'Radio Oriente',
                'nombre': suscripcion.nombre,
                'suscripcion_token': suscripcion.token_unsuscribe,
            }

            #renderizar el template html
            html_message = render_to_string('emails/nuevo_articulo.html', context)
  #versión texto plano como fallback

            #crear email con soporte html
            email = EmailMultiAlternatives(
                subject=subject,
  #versión texto plano
                from_email=from_email,
                to=[suscripcion.email]
            )

            #adjuntar versión html
            email.attach_alternative(html_message, "text/html")

            #agregar headers para el botón de desuscripcion de gmail
            backend_url = getattr(settings, 'BACKEND_URL', 'http://localhost:8000')
            unsubscribe_url = f"{backend_url}/api/contact/unsubscribe-token/?token={suscripcion.token_unsuscribe}"
            email.extra_headers = {
                'List-Unsubscribe': f'<{unsubscribe_url}>',
                'List-Unsubscribe-Post': 'List-Unsubscribe=One-Click'
            }

            #enviar
            email.send()
            sent_count += 1

        except Exception as e:
            print(f"Error al enviar email a {suscripcion.email}: {str(e)}")
            continue

    print(f"Newsletter enviado a {sent_count}/{suscriptores.count()} suscriptores para el artículo: {instance.titulo}")
