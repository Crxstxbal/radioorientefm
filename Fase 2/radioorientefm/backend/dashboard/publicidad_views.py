from django.http import FileResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
import os
import mimetypes

@csrf_exempt
@require_http_methods(["GET"])
def api_publicidad_media(request, campania_id):
    """sirve directamente la imagen de una campaña de publicidad. esta vista actúa como proxy para evitar bloqueos de adblockers"""
    try:
        from apps.publicidad.models import Publicidad, ItemSolicitudWeb
        import logging
        logger = logging.getLogger(__name__)

        #obtener la campaña
        pub = get_object_or_404(Publicidad, id=campania_id)
        logger.info(f"[PUBLICIDAD MEDIA] Campaña ID: {campania_id}")

        #obtener el archivo de media
        wc = getattr(pub, 'web_config', None)
        if not wc:
            logger.error(f"[PUBLICIDAD MEDIA] No se encontró web_config para campaña {campania_id}")
            return HttpResponse('No se encontró configuración web', status=404)

        archivo_media = getattr(wc, 'archivo_media', None)

        #si no hay archivo_media, intentar obtener desde itemsolicitudweb
        if not archivo_media:
            logger.info(f"[PUBLICIDAD MEDIA] No hay archivo_media, buscando en ItemSolicitudWeb")
            try:
                import re
                desc = getattr(pub, 'descripcion', '') or ''
                m = re.search(r'Item\s*#(\d+)', desc)
                if m:
                    item_id = int(m.group(1))
                    item = ItemSolicitudWeb.objects.get(id=item_id)
                    img = item.imagenes_web.order_by('orden', 'fecha_subida').first()
                    if img and getattr(img, 'imagen', None):
                        archivo_media = img.imagen
                        logger.info(f"[PUBLICIDAD MEDIA] Imagen encontrada desde Item #{item_id}")
            except Exception as e:
                logger.error(f"[PUBLICIDAD MEDIA] Error al buscar imagen en Item: {str(e)}")

        if not archivo_media:
            logger.error(f"[PUBLICIDAD MEDIA] No se encontró imagen para campaña {campania_id}")
            return HttpResponse('No se encontró archivo de medios', status=404)

        #obtener la ruta completa del archivo
        try:
            if hasattr(archivo_media, 'path'):
                file_path = archivo_media.path
            elif hasattr(archivo_media, 'url'):
                from django.conf import settings
                rel = str(archivo_media.url)
                #normalizar contra media_url si aplica
                if rel.startswith(settings.MEDIA_URL):
                    rel = rel[len(settings.MEDIA_URL):]
                #asegurar ruta relativa para evitar que os.path.join ignore media_root
                rel = rel.lstrip('/')
                file_path = os.path.join(settings.MEDIA_ROOT, rel)
            else:
                #si es string/relativo/absoluto
                from django.conf import settings
                rel = str(archivo_media)
                #normalizar separadores para analisis
                rel_norm = rel.replace('\\', '/').strip()
                #si es url completa, redirigir directamente
                if rel_norm.startswith('http://') or rel_norm.startswith('https://'):
                    logger.info(f"[PUBLICIDAD MEDIA] Redirigiendo a URL externa: {rel_norm}")
                    from django.http import HttpResponseRedirect
                    return HttpResponseRedirect(rel_norm)
                #si contiene segmento /media/, extraer parte relativa después de 'media/'
                if '/media/' in rel_norm:
                    rel_part = rel_norm.split('/media/', 1)[1]
                else:
                    rel_part = rel_norm
                    #si empieza con media_url, recortar
                    if rel_part.startswith(settings.MEDIA_URL):
                        rel_part = rel_part[len(settings.MEDIA_URL):]
                #asegurar ruta relativa (evitar que comience con '/' o 'c:/')
                while rel_part.startswith('/'):
                    rel_part = rel_part[1:]
                if ':' in rel_part and '/media/' in rel_norm:
                    rel_part = rel_norm.split('/media/', 1)[1]
                file_path = os.path.join(settings.MEDIA_ROOT, rel_part)

            #verificar que el archivo existe
            if not os.path.exists(file_path):
                logger.error(f"[PUBLICIDAD MEDIA] Archivo no encontrado: {file_path}")
                return HttpResponse('Archivo no encontrado', status=404)
                
            #determinar content-type
            content_type, _ = mimetypes.guess_type(file_path)
            if not content_type:
                content_type = 'application/octet-stream'

            #abrir y devolver el archivo
            response = FileResponse(open(file_path, 'rb'), content_type=content_type)

            #headers para evitar bloqueos de adblockers
            response['Cache-Control'] = 'public, max-age=3600'
            response['Access-Control-Allow-Origin'] = '*'

            logger.info(f"[PUBLICIDAD MEDIA] Imagen servida correctamente: {file_path}")
            return response

        except Exception as e:
            logger.error(f"[PUBLICIDAD MEDIA] Error al acceder al archivo: {str(e)}")
            #al acceder al archivo, intentar con la url
            try:
                media_url = getattr(archivo_media, 'url', None)
                if media_url:
                    logger.info(f"[PUBLICIDAD MEDIA] Redirigiendo a: {media_url}")
                    from django.http import HttpResponseRedirect
                    return HttpResponseRedirect(media_url)
            except Exception as e2:
                logger.error(f"[PUBLICIDAD MEDIA] Error al redirigir: {str(e2)}")
                pass

            return HttpResponse(f'Error al servir la imagen: {str(e)}', status=500)

    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"[PUBLICIDAD MEDIA] Error general: {str(e)}")
        import traceback
        traceback.print_exc()
        return HttpResponse(f'Error: {str(e)}', status=500)
