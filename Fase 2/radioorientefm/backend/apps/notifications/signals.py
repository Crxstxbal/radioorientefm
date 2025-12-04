#-*- coding: utf-8 -*-
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Notification

User = get_user_model()

def crear_notificacion_para_staff(tipo, titulo, mensaje, enlace=None, content_type=None, object_id=None):
    """crea notificaciones para todos los usuarios staff"""
    usuarios_staff = User.objects.filter(is_staff=True)

    notificaciones = []
    for usuario in usuarios_staff:
        notificacion = Notification.objects.create(
            usuario=usuario,
            tipo=tipo,
            titulo=titulo,
            mensaje=mensaje,
            enlace=enlace,
            content_type=content_type,
            object_id=object_id
        )
        notificaciones.append(notificacion)

    return notificaciones

#signal para contactos
@receiver(post_save, sender='contact.Contacto')
def notificar_nuevo_contacto(sender, instance, created, **kwargs):
    """notificar cuando se crea un nuevo mensaje de contacto"""
    if created:
        titulo = f"Nuevo mensaje de contacto de {instance.nombre}"
        mensaje = f"{instance.nombre} ({instance.email}) envio un mensaje de tipo '{instance.tipo_asunto.nombre}'"
        enlace = f"/dashboard/contactos/?id={instance.id}"

        crear_notificacion_para_staff(
            tipo='contacto',
            titulo=titulo,
            mensaje=mensaje,
            enlace=enlace,
            content_type='contacto',
            object_id=instance.id
        )

#signal para solicitudes de publicidad web
@receiver(post_save, sender='publicidad.SolicitudPublicidadWeb')
def notificar_nueva_solicitud_publicidad(sender, instance, created, **kwargs):
    """notificar cuando se crea una nueva solicitud de publicidad web"""
    if created:
        titulo = f"Nueva solicitud de publicidad: {instance.nombre_contacto or instance.usuario.email}"
        mensaje = (
            f"Solicitud #{instance.id} - Estado: {instance.get_estado_display()} - "
            f"{instance.fecha_inicio_solicitada} a {instance.fecha_fin_solicitada}"
        )
        enlace = f"/dashboard/publicidad/?id={instance.id}"

        crear_notificacion_para_staff(
            tipo='publicidad',
            titulo=titulo,
            mensaje=mensaje,
            enlace=enlace,
            content_type='solicitud_publicidad',
            object_id=instance.id
        )

#signal para bandas emergentes
@receiver(post_save, sender='emergente.BandaEmergente')
def notificar_nueva_banda(sender, instance, created, **kwargs):
    """notificar cuando se registra una nueva banda emergente"""
    if created:
        titulo = f"Nueva banda registrada: {instance.nombre_banda}"
        #el modelo tiene comuna, no ciudad. la comuna tiene una relación con ciudad
        ubicacion = 'ubicación no especificada'
        if instance.comuna:
            ubicacion = f"{instance.comuna.nombre}, {instance.comuna.ciudad.nombre}"
        mensaje = f"La banda '{instance.nombre_banda}' de {ubicacion} se ha registrado"
        enlace = f"/dashboard/emergentes/?id={instance.id}"

        crear_notificacion_para_staff(
            tipo='banda',
            titulo=titulo,
            mensaje=mensaje,
            enlace=enlace,
            content_type='banda',
            object_id=instance.id
        )

#signal para articulos
@receiver(post_save, sender='articulos.Articulo')
def notificar_nuevo_articulo(sender, instance, created, **kwargs):
    """notificar a otros admins cuando se crea un articulo"""
    if created and instance.autor:
        titulo = f"Nuevo articulo: {instance.titulo}"
        mensaje = f"{instance.autor.email} creo el articulo '{instance.titulo}'"
        enlace = f"/dashboard/articulos/?id={instance.id}"

        #notificar a todos los staff excepto al autor
        usuarios_staff = User.objects.filter(is_staff=True).exclude(id=instance.autor.id)

        for usuario in usuarios_staff:
            Notification.objects.create(
                usuario=usuario,
                tipo='articulo',
                titulo=titulo,
                mensaje=mensaje,
                enlace=enlace,
                content_type='articulo',
                object_id=instance.id
            )

#signal para programas
@receiver(post_save, sender='radio.Programa')
def notificar_cambio_programa(sender, instance, created, **kwargs):
    """notificar cuando se crea o modifica un programa"""
    if created:
        titulo = f"Nuevo programa: {instance.nombre}"
        mensaje = f"Se creo el programa '{instance.nombre}' en el horario de programacion"
    else:
        titulo = f"Programa actualizado: {instance.nombre}"
        mensaje = f"El programa '{instance.nombre}' ha sido modificado"

    enlace = f"/dashboard/programas/?id={instance.id}"

    crear_notificacion_para_staff(
        tipo='programa',
        titulo=titulo,
        mensaje=mensaje,
        enlace=enlace,
        content_type='programa',
        object_id=instance.id
    )

#signal para horarios de programas
@receiver(post_save, sender='radio.HorarioPrograma')
def notificar_cambio_horario(sender, instance, created, **kwargs):
    """notificar cuando se crea o modifica un horario de programa"""
    if created:
        titulo = f"Nuevo horario para: {instance.programa.nombre}"
        mensaje = f"Se anadio un nuevo horario ({instance.get_dia_semana_display()}, {instance.hora_inicio.strftime('%H:%M')}) para el programa '{instance.programa.nombre}'"
    else:
        titulo = f"Horario actualizado: {instance.programa.nombre}"
        mensaje = f"Se modifico el horario del {instance.get_dia_semana_display()} para '{instance.programa.nombre}'"

    enlace = f"/dashboard/radio/?programa={instance.programa.id}"

    crear_notificacion_para_staff(
        tipo='programa',
        titulo=titulo,
        mensaje=mensaje,
        enlace=enlace,
        content_type='horario',
        object_id=instance.id
    )

#signal para suscripciones
@receiver(post_save, sender='contact.Suscripcion')
def notificar_nueva_suscripcion(sender, instance, created, **kwargs):
    """notificar cuando hay una nueva suscripcion"""
    if created:
        titulo = f"Nueva suscripcion: {instance.email}"
        mensaje = f"{instance.nombre or 'Usuario'} ({instance.email}) se suscribio al newsletter"
        enlace = f"/dashboard/suscripciones/?id={instance.id}"

        crear_notificacion_para_staff(
            tipo='suscripcion',
            titulo=titulo,
            mensaje=mensaje,
            enlace=enlace,
            content_type='suscripcion',
            object_id=instance.id
        )
