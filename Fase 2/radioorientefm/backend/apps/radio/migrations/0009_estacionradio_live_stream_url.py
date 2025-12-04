#generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('radio', '0008_alter_programa_estacion'),
    ]

    operations = [
        migrations.AddField(
            model_name='estacionradio',
            name='live_stream_url',
            field=models.URLField(blank=True, help_text='URL de YouTube, Facebook Live u otra plataforma para transmisión en vivo', max_length=500, null=True, verbose_name='URL de transmisión en vivo'),
        ),
    ]
