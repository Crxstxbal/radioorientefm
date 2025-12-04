#generated manually to add foreign key relationships

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def migrate_existing_data(apps, schema_editor):
    """migrar id_usuario existentes al nuevo campo usuario"""
    ChatMessage = apps.get_model('chat', 'ChatMessage')
    InfraccionUsuario = apps.get_model('chat', 'InfraccionUsuario')
    User = apps.get_model(settings.AUTH_USER_MODEL)

    #obtener el primer usuario staff como fallback
    admin_user = User.objects.filter(is_staff=True).first()
    if not admin_user:
        #si no hay staff, usar el primer usuario
        admin_user = User.objects.first()

    if not admin_user:
        print("⚠️  No hay usuarios en la base de datos. Se deben crear usuarios antes de migrar.")
        return

    #migrar mensajes
    for mensaje in ChatMessage.objects.all():
        try:
            #intentar obtener el usuario por id_usuario
            usuario = User.objects.get(id=mensaje.id_usuario_old)
            mensaje.usuario_temp = usuario
        except User.DoesNotExist:
            #si no existe, usar admin como fallback
            mensaje.usuario_temp = admin_user
        mensaje.save()

    #migrar infracciones
    for infraccion in InfraccionUsuario.objects.all():
        try:
            #intentar obtener el usuario por id_usuario
            usuario = User.objects.get(id=infraccion.id_usuario_old)
            infraccion.usuario_temp = usuario
        except User.objects.model.DoesNotExist:
            #si no existe, usar admin como fallback
            infraccion.usuario_temp = admin_user
        infraccion.save()


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0002_contentfilterconfig_infraccionusuario_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        #paso 1: renombrar columnas antiguas
        migrations.RenameField(
            model_name='chatmessage',
            old_name='id_usuario',
            new_name='id_usuario_old',
        ),
        migrations.RenameField(
            model_name='infraccionusuario',
            old_name='id_usuario',
            new_name='id_usuario_old',
        ),

        #paso 2: agregar nuevos campos como nullable
        migrations.AddField(
            model_name='chatmessage',
            name='usuario_temp',
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='mensajes_chat_temp',
                to=settings.AUTH_USER_MODEL,
                help_text="Usuario que envió el mensaje"
            ),
        ),
        migrations.AddField(
            model_name='infraccionusuario',
            name='usuario_temp',
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='infracciones_chat_temp',
                to=settings.AUTH_USER_MODEL,
                help_text="Usuario que cometió la infracción"
            ),
        ),
        migrations.AddField(
            model_name='infraccionusuario',
            name='mensaje',
            field=models.ForeignKey(
                blank=True,
                help_text='Mensaje que causó la infracción (si aplica)',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='infracciones',
                to='chat.chatmessage',
            ),
        ),

        #paso 3: migrar datos
        migrations.RunPython(migrate_existing_data, migrations.RunPython.noop),

        #paso 4: eliminar campos antiguos
        migrations.RemoveField(
            model_name='chatmessage',
            name='id_usuario_old',
        ),
        migrations.RemoveField(
            model_name='infraccionusuario',
            name='id_usuario_old',
        ),

        #paso 5: renombrar campos nuevos al nombre final y hacerlos not-null
        migrations.RenameField(
            model_name='chatmessage',
            old_name='usuario_temp',
            new_name='usuario',
        ),
        migrations.RenameField(
            model_name='infraccionusuario',
            old_name='usuario_temp',
            new_name='usuario',
        ),

        #paso 6: modificar el campo para que sea not null y tenga db_column
        migrations.AlterField(
            model_name='chatmessage',
            name='usuario',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='mensajes_chat',
                to=settings.AUTH_USER_MODEL,
                db_column='id_usuario',
                help_text="Usuario que envió el mensaje"
            ),
        ),
        migrations.AlterField(
            model_name='infraccionusuario',
            name='usuario',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='infracciones_chat',
                to=settings.AUTH_USER_MODEL,
                db_column='id_usuario',
                help_text="Usuario que cometió la infracción"
            ),
        ),

        #paso 7: agregar índices
        migrations.AddIndex(
            model_name='chatmessage',
            index=models.Index(fields=['usuario'], name='mensajes_usuario_idx'),
        ),
        migrations.AddIndex(
            model_name='chatmessage',
            index=models.Index(fields=['fecha_envio'], name='mensajes_fecha_idx'),
        ),
        migrations.AddIndex(
            model_name='chatmessage',
            index=models.Index(fields=['sala'], name='mensajes_sala_idx'),
        ),
        migrations.AddIndex(
            model_name='infraccionusuario',
            index=models.Index(fields=['usuario'], name='infracciones_usuario_idx'),
        ),
        migrations.AddIndex(
            model_name='infraccionusuario',
            index=models.Index(fields=['fecha_infraccion'], name='infracciones_fecha_idx'),
        ),
        migrations.AddIndex(
            model_name='infraccionusuario',
            index=models.Index(fields=['tipo_infraccion'], name='infracciones_tipo_idx'),
        ),
    ]
