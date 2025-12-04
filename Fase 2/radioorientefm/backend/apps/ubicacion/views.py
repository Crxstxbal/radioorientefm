from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from .models import Pais, Ciudad, Comuna
from .serializers import PaisSerializer, CiudadSerializer, ComunaSerializer, ComunaDetailSerializer
import requests
from django.db import transaction

#helpers para consultar api externa divpa con fallback
DIVPA_BASE = "https://apis.digital.gob.cl/dpa"

def _fetch_divpa_regiones():
    """obtiene regiones desde api divpa"""
    url = f"{DIVPA_BASE}/regiones" 
    #se elimina verify=false para mayor seguridad en producción
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    return resp.json()

def _fetch_divpa_comunas_por_region(codigo_region):
    """obtiene comunas por codigo de region desde api divpa"""
    url = f"{DIVPA_BASE}/regiones/{codigo_region}/comunas"
    #se elimina verify=false para mayor seguridad en producción
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    return resp.json()

class PaisViewSet(viewsets.ModelViewSet):
    """viewset para países"""
    queryset = Pais.objects.all()
    serializer_class = PaisSerializer
    permission_classes = [permissions.AllowAny]
    
    @action(detail=False, methods=['post'])
    def reiniciar_datos_chile(self, request):
        """limpia y recarga todos los datos de chile desde la api externa divpa"""
        try:
            with transaction.atomic():
                #eliminar datos de ubicacion existentes para chile y recrear
                #esto eliminará en cascada ciudades y comunas
                Pais.objects.filter(nombre='Chile').delete()
                
                #crear chile
                chile = Pais.objects.create(nombre='Chile')
                
                regiones_creadas = 0
                comunas_creadas = 0
                
                #cargar regiones desde la api
                regiones_data = _fetch_divpa_regiones()
                
                for region_data in regiones_data:
                    nombre_region = region_data.get('nombre')
                    codigo_region = region_data.get('codigo')
                    
                    if not nombre_region or not codigo_region:
                        continue

                    #crear región como ciudad
                    ciudad, created = Ciudad.objects.get_or_create(
                        nombre=nombre_region,
                        pais=chile
                    )
                    if created:
                        regiones_creadas += 1
                    
                    #cargar comunas para esta región desde la api
                    comunas_data = _fetch_divpa_comunas_por_region(codigo_region)
                    for comuna_data in comunas_data:
                        nombre_comuna = comuna_data.get('nombre')
                        if not nombre_comuna:
                            continue
                        
                        _, created = Comuna.objects.get_or_create(
                            nombre=nombre_comuna,
                            ciudad=ciudad
                        )
                        if created:
                            comunas_creadas += 1
            
            return Response({
                'message': 'Datos de Chile cargados correctamente desde la API externa',
                'regiones_creadas': regiones_creadas,
                'comunas_creadas': comunas_creadas
            }, status=status.HTTP_201_CREATED)

        except requests.RequestException as e:
            return Response({
                'error': f'Error al conectar con la API externa: {str(e)}'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except Exception as e:
            return Response({
                'error': f'Error al procesar los datos: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CiudadViewSet(viewsets.ReadOnlyModelViewSet):
    """viewset para ciudades (solo lectura)"""
    queryset = Ciudad.objects.select_related('pais').all()
    serializer_class = CiudadSerializer
    permission_classes = [permissions.AllowAny]  #permite que cualquiera consulte las ciudades
    
    @action(detail=False, methods=['get'])
    def por_pais(self, request):
        """obtener ciudades por país directamente desde la base de datos"""
        pais_id = request.query_params.get('pais_id')
        if pais_id:
            ciudades = self.queryset.filter(pais_id=pais_id)
            serializer = self.get_serializer(ciudades, many=True)
            return Response(serializer.data)
        return Response([])
    
    @action(detail=False, methods=['post'])
    def cargar_desde_api(self, request):
        """cargar regiones de chile desde api externa y guardar en bd"""
        try:
            #api pública de regiones de chile
            api_url = "https://apis.digital.gob.cl/dpa/regiones"
            response = requests.get(api_url, timeout=10)
            response.raise_for_status()
            
            regiones_data = response.json()
            
            #obtener o crear chile
            chile, _ = Pais.objects.get_or_create(nombre='Chile')
            
            ciudades_creadas = 0
            with transaction.atomic():
                for region in regiones_data:
                    nombre_region = region.get('nombre', '')
                    if nombre_region:
                        _, created = Ciudad.objects.get_or_create(
                            nombre=nombre_region,
                            pais=chile
                        )
                        if created:
                            ciudades_creadas += 1
            
            return Response({
                'message': f'Se cargaron {ciudades_creadas} regiones desde la API',
                'total_regiones': len(regiones_data)
            }, status=status.HTTP_201_CREATED)
            
        except requests.RequestException as e:
            return Response({
                'error': f'Error al conectar con la API: {str(e)}'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except Exception as e:
            return Response({
                'error': f'Error al procesar datos: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ComunaViewSet(viewsets.ReadOnlyModelViewSet):
    """viewset para comunas (solo lectura)"""
    queryset = Comuna.objects.select_related('ciudad__pais').all()
    serializer_class = ComunaSerializer
    permission_classes = [permissions.AllowAny]
    
    @action(detail=False, methods=['get'])
    def por_ciudad(self, request):
        """obtener comunas por ciudad directamente desde la base de datos"""
        ciudad_id = request.query_params.get('ciudad_id')
        if ciudad_id:
            comunas = self.queryset.filter(ciudad_id=ciudad_id)
            serializer = ComunaDetailSerializer(comunas, many=True)
            return Response(serializer.data)
        return Response([])
    
    @action(detail=False, methods=['post'])
    def cargar_desde_api(self, request):
        """cargar comunas de chile desde api externa y guardar en bd"""
        try:
            #api pública de regiones de chile
            api_url = "https://apis.digital.gob.cl/dpa/regiones"
            response = requests.get(api_url, timeout=10)
            response.raise_for_status()
            
            regiones_data = response.json()
            
            #obtener chile
            chile = Pais.objects.get(nombre='Chile')
            
            comunas_creadas = 0
            comunas_totales = 0
            
            with transaction.atomic():
                for region in regiones_data:
                    codigo_region = region.get('codigo', '')
                    nombre_region = region.get('nombre', '')
                    
                    if not codigo_region or not nombre_region:
                        continue
                    
                    #obtener o crear la región como ciudad
                    ciudad, _ = Ciudad.objects.get_or_create(
                        nombre=nombre_region,
                        pais=chile
                    )
                    
                    #obtener comunas de esta región
                    comunas_url = f"https://apis.digital.gob.cl/dpa/regiones/{codigo_region}/comunas"
                    comunas_response = requests.get(comunas_url, timeout=10)
                    comunas_response.raise_for_status()
                    
                    comunas_data = comunas_response.json()
                    comunas_totales += len(comunas_data)
                    
                    for comuna in comunas_data:
                        nombre_comuna = comuna.get('nombre', '')
                        if nombre_comuna:
                            _, created = Comuna.objects.get_or_create(
                                nombre=nombre_comuna,
                                ciudad=ciudad
                            )
                            if created:
                                comunas_creadas += 1
            
            return Response({
                'message': f'Se cargaron {comunas_creadas} comunas desde la API',
                'total_comunas': comunas_totales,
                'nuevas_comunas': comunas_creadas
            }, status=status.HTTP_201_CREATED)
            
        except Pais.DoesNotExist:
            return Response({
                'error': 'Primero debes cargar las regiones. País Chile no encontrado.'
            }, status=status.HTTP_400_BAD_REQUEST)
        except requests.RequestException as e:
            return Response({
                'error': f'Error al conectar con la API: {str(e)}'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except Exception as e:
            return Response({
                'error': f'Error al procesar datos: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)