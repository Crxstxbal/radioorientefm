from django.core.management.base import BaseCommand
from django.db import transaction
import requests
import time

from apps.ubicacion.models import Pais, Ciudad, Comuna

# Replicamos las funciones de la API aquí para que el comando sea independiente
DIVPA_BASE = "https://apis.digital.gob.cl/dpa"

# Añadimos un User-Agent para simular un navegador y evitar bloqueos.
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def _fetch_divpa_regiones(verify_ssl=True):
    """Obtiene regiones desde API DIVPA. Lanza excepción si falla."""
    url = f"{DIVPA_BASE}/regiones"
    # Usamos el encabezado User-Agent en la petición
    resp = requests.get(url, timeout=30, verify=verify_ssl, headers=HEADERS)
    resp.raise_for_status()
    return resp.json()

def _fetch_divpa_comunas_por_region(codigo_region, verify_ssl=True):
    """Obtiene comunas por código de región desde API DIVPA. Lanza excepción si falla."""
    url = f"{DIVPA_BASE}/regiones/{codigo_region}/comunas"
    # Usamos el encabezado User-Agent en la petición
    resp = requests.get(url, timeout=30, verify=verify_ssl, headers=HEADERS)
    resp.raise_for_status()
    return resp.json()


class Command(BaseCommand):
    help = 'Limpia y recarga todos los datos de regiones y comunas de Chile desde la API oficial DIVPA.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--no-ssl-verify',
            action='store_true',
            help='Desactiva la verificación del certificado SSL al conectar con la API externa.',
        )

    def handle(self, *args, **options):
        verify_ssl = not options['no_ssl_verify']
        start_time = time.time()

        self.stdout.write(self.style.WARNING('Iniciando la sincronización de datos de ubicación de Chile...'))
        if not verify_ssl:
            self.stdout.write(self.style.NOTICE('ADVERTENCIA: La verificación SSL está desactivada.'))

        try:
            with transaction.atomic():
                self.stdout.write('-> Eliminando datos antiguos de Chile...')
                Pais.objects.filter(nombre='Chile').delete()

                self.stdout.write('-> Creando país "Chile"...', ending=' ')
                chile = Pais.objects.create(nombre='Chile')
                self.stdout.write(self.style.SUCCESS('OK'))

                self.stdout.write('-> Obteniendo regiones desde la API...', ending=' ')
                regiones_data = _fetch_divpa_regiones(verify_ssl=verify_ssl)
                self.stdout.write(self.style.SUCCESS(f'OK ({len(regiones_data)} encontradas)'))

                ciudades_para_crear = []
                for region_data in regiones_data:
                    nombre_region = region_data.get('nombre')
                    if nombre_region:
                        ciudades_para_crear.append(Ciudad(nombre=nombre_region, pais=chile))
                
                Ciudad.objects.bulk_create(ciudades_para_crear)
                self.stdout.write(self.style.SUCCESS(f'   - {len(ciudades_para_crear)} regiones guardadas como ciudades.'))

                # Mapear nombres de ciudades a objetos para la creación de comunas
                ciudades_map = {c.nombre: c for c in Ciudad.objects.filter(pais=chile)}
                comunas_para_crear = []
                total_comunas = 0

                for i, region_data in enumerate(regiones_data):
                    nombre_region = region_data.get('nombre', 'N/A')
                    codigo_region = region_data.get('codigo')
                    self.stdout.write(f'   - Obteniendo comunas para "{nombre_region}" ({i+1}/{len(regiones_data)})...', ending=' ')
                    
                    if not codigo_region or nombre_region not in ciudades_map:
                        self.stdout.write(self.style.ERROR('SALTADO'))
                        continue

                    ciudad_obj = ciudades_map[nombre_region]
                    comunas_data = _fetch_divpa_comunas_por_region(codigo_region, verify_ssl=verify_ssl)
                    self.stdout.write(self.style.SUCCESS(f'OK ({len(comunas_data)} encontradas)'))

                    for comuna_data in comunas_data:
                        nombre_comuna = comuna_data.get('nombre')
                        if nombre_comuna:
                            comunas_para_crear.append(Comuna(nombre=nombre_comuna, ciudad=ciudad_obj))
                            total_comunas += 1
                
                self.stdout.write(f'-> Guardando {len(comunas_para_crear)} comunas en la base de datos...', ending=' ')
                Comuna.objects.bulk_create(comunas_para_crear)
                self.stdout.write(self.style.SUCCESS('OK'))
            
            elapsed_time = time.time() - start_time
            self.stdout.write(self.style.SUCCESS(
                f'\n¡Sincronización completada! Se guardaron {len(ciudades_para_crear)} regiones y {total_comunas} comunas. '
                f'Tiempo: {elapsed_time:.2f} segundos.'
            ))

        except requests.RequestException as e:
            self.stderr.write(self.style.ERROR(f'Error de red al conectar con la API: {e}'))
            self.stderr.write(self.style.NOTICE('TIP: El error parece ser de conexión o SSL. Intenta ejecutar el comando con la opción --no-ssl-verify'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Ocurrió un error inesperado: {e}'))
