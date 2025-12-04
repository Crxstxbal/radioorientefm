from django.core.management.base import BaseCommand
from apps.contact.models import Estado, TipoAsunto


class Command(BaseCommand):
    help = 'Inicializa datos base para el módulo de contacto (Estados y Tipos de Asunto)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Iniciando creación de datos base para Contactos...'))

        #crear estados para contacto
        estados_contacto = [
            {'nombre': 'Recibida', 'descripcion': 'Mensaje recibido, pendiente de revisión'},
            {'nombre': 'En Revisión', 'descripcion': 'Mensaje en proceso de revisión'},
            {'nombre': 'Respondida', 'descripcion': 'Mensaje respondido al usuario'},
            {'nombre': 'Archivada', 'descripcion': 'Mensaje archivado'},
        ]

        created_estados = 0
        for estado_data in estados_contacto:
            estado, created = Estado.objects.get_or_create(
                nombre=estado_data['nombre'],
                tipo_entidad='contacto',
                defaults={'descripcion': estado_data['descripcion']}
            )
            if created:
                created_estados += 1
                self.stdout.write(
                    self.style.SUCCESS(f'  ✓ Estado creado: {estado.nombre}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'  - Estado ya existe: {estado.nombre}')
                )

        #crear tipos de asunto
        tipos_asunto = [
            'Consulta General',
            'Publicidad',
            'Programación',
            'Técnico',
            'Sugerencias',
            'Reclamos',
            'Felicitaciones',
            'Patrocinios',
        ]

        created_tipos = 0
        for tipo_nombre in tipos_asunto:
            tipo, created = TipoAsunto.objects.get_or_create(nombre=tipo_nombre)
            if created:
                created_tipos += 1
                self.stdout.write(
                    self.style.SUCCESS(f'  ✓ Tipo de Asunto creado: {tipo.nombre}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'  - Tipo de Asunto ya existe: {tipo.nombre}')
                )

        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS(f'✓ Proceso completado'))
        self.stdout.write(self.style.SUCCESS(f'  - Estados creados: {created_estados}'))
        self.stdout.write(self.style.SUCCESS(f'  - Tipos de Asunto creados: {created_tipos}'))
        self.stdout.write('='*50 + '\n')
