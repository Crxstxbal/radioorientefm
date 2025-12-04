from django.db import migrations, models
import django.db.models.deletion
import re


def link_publicidad_to_solicitud(apps, schema_editor):
    Publicidad = apps.get_model('publicidad', 'Publicidad')
    SolicitudPublicidadWeb = apps.get_model('publicidad', 'SolicitudPublicidadWeb')
    ItemSolicitudWeb = apps.get_model('publicidad', 'ItemSolicitudWeb')

    # 1) usar el campo OneToOne actual como fuente directa
    for solicitud in SolicitudPublicidadWeb.objects.exclude(publicacion__isnull=True):
        pub = solicitud.publicacion
        if pub and pub.tipo == 'WEB' and getattr(pub, 'solicitud_web_origen_id', None) is None:
            pub.solicitud_web_origen = solicitud
            pub.save(update_fields=['solicitud_web_origen'])

    # 2) para el resto de campañas WEB, inferir por la descripción "Item #id"
    for pub in Publicidad.objects.filter(tipo='WEB', solicitud_web_origen__isnull=True):
        desc = pub.descripcion or ''
        m = re.search(r'Item\s*#(\d+)', desc)
        if not m:
            continue
        item_id = int(m.group(1))
        try:
            item = ItemSolicitudWeb.objects.select_related('solicitud').get(id=item_id)
        except ItemSolicitudWeb.DoesNotExist:
            continue
        solicitud = getattr(item, 'solicitud', None)
        if solicitud and getattr(pub, 'solicitud_web_origen_id', None) is None:
            pub.solicitud_web_origen = solicitud
            pub.save(update_fields=['solicitud_web_origen'])


def unlink_publicidad_from_solicitud(apps, schema_editor):
    # reversa suave: simplemente limpiar el FK
    Publicidad = apps.get_model('publicidad', 'Publicidad')
    Publicidad.objects.update(solicitud_web_origen=None)


class Migration(migrations.Migration):

    dependencies = [
        ('publicidad', '0009_solicitudpublicidadweb_aprobado_por_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='publicidad',
            name='solicitud_web_origen',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='campanias_web',
                to='publicidad.solicitudpublicidadweb',
                verbose_name='Solicitud Web de origen',
            ),
        ),
        migrations.RunPython(link_publicidad_to_solicitud, unlink_publicidad_from_solicitud),
    ]
