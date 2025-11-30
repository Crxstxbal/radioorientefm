from django.db import migrations, models
import django.db.models.deletion


def populate_tipo_ubicacion(apps, schema_editor):
    TipoUbicacion = apps.get_model('publicidad', 'TipoUbicacion')
    UbicacionPublicidadWeb = apps.get_model('publicidad', 'UbicacionPublicidadWeb')

    # Crear tipos a partir de los códigos existentes en el campo CharField 'tipo'
    existentes = (
        UbicacionPublicidadWeb.objects
        .values_list('tipo', flat=True)
        .distinct()
    )

    # Mapeo opcional para nombres amigables
    nombres_map = {
        'panel_izquierdo': 'Panel Lateral Izquierdo',
        'panel_derecho': 'Panel Lateral Derecho',
        'banner_superior_home': 'Banner Superior Home (debajo navbar)',
        'banner_articulos': 'Banner Debajo de Últimos Artículos',
    }

    codigo_to_obj = {}
    for codigo in existentes:
        if codigo is None:
            continue
        nombre = nombres_map.get(codigo, (codigo or '').replace('_', ' ').title())
        obj, _ = TipoUbicacion.objects.get_or_create(
            codigo=codigo,
            defaults={
                'nombre': nombre,
                'descripcion': f'Ubicación de tipo {nombre}',
                'activo': True,
            }
        )
        codigo_to_obj[codigo] = obj

    # Poblar el campo temporal FK con el id correspondiente
    for u in UbicacionPublicidadWeb.objects.all():
        tipo_fk = codigo_to_obj.get(u.tipo)
        if tipo_fk:
            # Asignar al campo temporal
            setattr(u, 'tipo_temp_id', tipo_fk.id)
            u.save(update_fields=['tipo_temp'])


class Migration(migrations.Migration):

    dependencies = [
        ('publicidad', '0009_solicitudpublicidadweb_aprobado_por_and_more'),
    ]

    operations = [
        # 1) Crear el nuevo modelo
        migrations.CreateModel(
            name='TipoUbicacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.SlugField(help_text='Identificador único en minúsculas y sin espacios (ej: banner_principal)', unique=True, verbose_name='Código del Tipo')),
                ('nombre', models.CharField(help_text='Nombre descriptivo del tipo de ubicación', max_length=100, verbose_name='Nombre del Tipo')),
                ('descripcion', models.TextField(blank=True, help_text='Descripción detallada de este tipo de ubicación', null=True, verbose_name='Descripción')),
                ('activo', models.BooleanField(default=True, help_text='¿Este tipo de ubicación está disponible para su uso?', verbose_name='¿Activo?')),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('ultima_actualizacion', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Tipo de Ubicación',
                'verbose_name_plural': 'Tipos de Ubicación',
                'ordering': ['nombre'],
            },
        ),

        # 2) Agregar un campo temporal FK
        migrations.AddField(
            model_name='ubicacionpublicidadweb',
            name='tipo_temp',
            field=models.ForeignKey(null=True, blank=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='publicidad.tipoubicacion'),
        ),

        # 3) Migrar datos del CharField al FK temporal
        migrations.RunPython(populate_tipo_ubicacion, migrations.RunPython.noop),

        # 4) Eliminar el campo CharField original
        migrations.RemoveField(
            model_name='ubicacionpublicidadweb',
            name='tipo',
        ),

        # 5) Renombrar el campo temporal a definitivo
        migrations.RenameField(
            model_name='ubicacionpublicidadweb',
            old_name='tipo_temp',
            new_name='tipo',
        ),

        # 6) Ajustar opciones del campo definitivo
        migrations.AlterField(
            model_name='ubicacionpublicidadweb',
            name='tipo',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='ubicaciones', to='publicidad.tipoubicacion', verbose_name='Tipo de Ubicación'),
        ),
    ]
