from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import logging
from .models import Articulo
from apps.contact.models import Suscripcion

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=Articulo)
def guardar_estado_anterior(sender, instance, **kwargs):
    """guarda el estado anterior de publicado para detectar cambios"""
    if instance.pk:
        try:
            old_instance = Articulo.objects.get(pk=instance.pk)
            instance._publicado_anterior = old_instance.publicado
        except Articulo.DoesNotExist:
            instance._publicado_anterior = False
    else:
        instance._publicado_anterior = False


@receiver(post_save, sender=Articulo)
def enviar_newsletter_articulo(sender, instance, created, **kwargs):
    """envía un email html a todos los suscriptores activos cuando se publica un artículo.
    se envía si:
    - es un artículo nuevo y está publicado, o
    - es un artículo existente que acaba de cambiar a publicado
    """
    #verificar si debemos enviar el newsletter
    publicado_anterior = getattr(instance, '_publicado_anterior', False)
    
    #enviar si: (es nuevo Y publicado) O (cambió de no publicado a publicado)
    debe_enviar = (
        (created and instance.publicado) or 
        (not created and not publicado_anterior and instance.publicado)
    )
    
    if not debe_enviar:
        logger.info(f"No se envía newsletter para '{instance.titulo}': created={created}, publicado={instance.publicado}, publicado_anterior={publicado_anterior}")
        return
    
    logger.info(f"Iniciando envío de newsletter para artículo: {instance.titulo}")

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
                'imagen_articulo': imagen_url,  #url completa de la imagen
                'site_url': settings.FRONTEND_URL or 'http://localhost:3000',
                'radio_name': 'Radio Oriente',
                'nombre': suscripcion.nombre,
                'suscripcion_token': suscripcion.token_unsuscribe,
            }

            #renderizar el template html
            html_message = render_to_string('emails/nuevo_articulo.html', context)
            plain_message = strip_tags(html_message)  #versión texto plano como fallback

            #crear email con soporte html
            email = EmailMultiAlternatives(
                subject=subject,
                body=plain_message,  #versión texto plano
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
