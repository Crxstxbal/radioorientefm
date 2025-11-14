from django.core.management.base import BaseCommand
from apps.publicidad.models import UbicacionPublicidad
from decimal import Decimal


class Command(BaseCommand):
    help = 'Crea las 4 ubicaciones de publicidad predefinidas'

    def handle(self, *args, **options):
        ubicaciones = [
            {
                'nombre': 'Panel Lateral Izquierdo',
                'tipo': 'panel_izquierdo',
                'descripcion': 'Espacio vertical a la izquierda del contenido principal. Visible durante toda la navegación en el Home.',
                'dimensiones': '160x600',
                'precio_mensual': Decimal('199.00'),
                'activo': True,
                'orden': 1
            },
            {
                'nombre': 'Panel Lateral Derecho',
                'tipo': 'panel_derecho',
                'descripcion': 'Espacio vertical a la derecha del contenido principal. Alta tasa de interacción durante la navegación en el Home.',
                'dimensiones': '300x600',
                'precio_mensual': Decimal('249.00'),
                'activo': True,
                'orden': 2
            },
            {
                'nombre': 'Banner Superior Home',
                'tipo': 'banner_superior_home',
                'descripcion': 'Banner horizontal debajo del navbar, visible solo en la página de inicio. Máxima visibilidad al entrar al sitio.',
                'dimensiones': '728x90',
                'precio_mensual': Decimal('299.00'),
                'activo': True,
                'orden': 3
            },
            {
                'nombre': 'Banner Debajo de Últimos Artículos',
                'tipo': 'banner_articulos',
                'descripcion': 'Banner grande debajo de la sección de últimos artículos en el Home. Alto impacto visual.',
                'dimensiones': '970x250',
                'precio_mensual': Decimal('349.00'),
                'activo': True,
                'orden': 4
            },
        ]

        creadas = 0
        actualizadas = 0

        for ubicacion_data in ubicaciones:
            ubicacion, created = UbicacionPublicidad.objects.update_or_create(
                tipo=ubicacion_data['tipo'],
                defaults=ubicacion_data
            )
            
            if created:
                creadas += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Creada: {ubicacion.nombre}')
                )
            else:
                actualizadas += 1
                self.stdout.write(
                    self.style.WARNING(f'↻ Actualizada: {ubicacion.nombre}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Proceso completado: {creadas} creadas, {actualizadas} actualizadas'
            )
        )
