"""utilidades para analisis de contenido con machine learning"""
import os
import re
from typing import Dict, Tuple
from .models import ContentFilterConfig, PalabraProhibida, InfraccionUsuario


class ContentAnalyzer:
    """analizador de contenido con ml para detectar mensajes ofensivos"""

    def __init__(self):
        """inicializar modelo ml de detoxify para español"""
        #detectar si esta en Render
        disable_detoxify = os.getenv('DISABLE_DETOXIFY', 'false').lower() == 'true'
        is_render = os.getenv('RENDER', 'false').lower() == 'true'
        
        #desactivar Detoxify en Render automáticamente o si está configurado
        if disable_detoxify or is_render:
            print("Detoxify desactivado (Render o configuración manual)")
            self.model = None
            self.disabled = True
        else:
            #solo cargar en localhost
            try:
                from detoxify import Detoxify
                print("Cargando modelo Detoxify para análisis de toxicidad...")
                self.model = Detoxify('multilingual')
                self.disabled = False
                print("Detoxify cargado exitosamente")
            except Exception as e:
                print(f"Error al cargar modelo Detoxify: {e}")
                self.model = None
                self.disabled = True

    def analyze_message(self, contenido: str, id_usuario: int, usuario_nombre: str) -> Dict:
        """analizar mensaje y determinar si debe ser bloqueado returns: dict con: - allowed: bool - si el mensaje puede publicarse - reason: str - razón del bloqueo (si aplica) - score: float - score de toxicidad (0.0 - 1.0) - infraction_type: str - tipo de infracción"""
        config = ContentFilterConfig.get_config()

        #si el filtro está desactivado, permitir todo
        if not config.activo:
            return {
                'allowed': True,
                'reason': None,
                'score': 0.0,
                'infraction_type': None
            }

        #1. verificar enlaces (si está activado)
        if config.bloquear_enlaces:
            if self._contains_links(contenido):
                self._register_infraction(
                    id_usuario, usuario_nombre, contenido,
                    'enlace_prohibido', 1.0, config.modo_accion
                )
                return {
                    'allowed': False,
                    'reason': 'Enlaces no permitidos en el chat',
                    'score': 1.0,
                    'infraction_type': 'enlace_prohibido'
                }

        #2. verificar palabras prohibidas personalizadas
        palabra_encontrada = self._check_prohibited_words(contenido)
        if palabra_encontrada:
            self._register_infraction(
                id_usuario, usuario_nombre, contenido,
                'palabra_prohibida', 1.0, config.modo_accion
            )
            return {
                'allowed': False,
                'reason': f'Contenido no permitido: palabra prohibida detectada',
                'score': 1.0,
                'infraction_type': 'palabra_prohibida'
            }

        #3. analisis ml de toxicidad
        toxicity_score = self._analyze_toxicity(contenido)

        if toxicity_score >= config.umbral_toxicidad:
            self._register_infraction(
                id_usuario, usuario_nombre, contenido,
                'toxicidad_ml', toxicity_score, config.modo_accion
            )

            #verificar si debe bloquearse automáticamente
            if self._should_auto_block(id_usuario, config):
                return {
                    'allowed': False,
                    'reason': 'Has acumulado demasiadas infracciones. Tu cuenta ha sido bloqueada automáticamente.',
                    'score': toxicity_score,
                    'infraction_type': 'toxicidad_ml',
                    'auto_blocked': True
                }

            if config.modo_accion == 'bloquear':
                return {
                    'allowed': False,
                    'reason': 'Mensaje bloqueado por contenido inapropiado',
                    'score': toxicity_score,
                    'infraction_type': 'toxicidad_ml'
                }
            elif config.modo_accion == 'advertir':
                return {
                    'allowed': True,
                    'reason': None,
                    'score': toxicity_score,
                    'infraction_type': 'toxicidad_ml',
                    'warning': f'Advertencia: Tu mensaje ha sido marcado como potencialmente ofensivo (score: {toxicity_score:.2f})'
                }

        #mensaje limpio
        return {
            'allowed': True,
            'reason': None,
            'score': toxicity_score,
            'infraction_type': None
        }

    def _contains_links(self, text: str) -> bool:
        """detectar si el texto contiene urls"""
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        www_pattern = r'www\.[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'

        return bool(re.search(url_pattern, text, re.IGNORECASE) or
                   re.search(www_pattern, text, re.IGNORECASE))

    def _check_prohibited_words(self, text: str) -> bool:
        """verificar si el texto contiene palabras prohibidas"""
        palabras = PalabraProhibida.objects.filter(activa=True)
        text_lower = text.lower()

        for palabra_obj in palabras:
            #buscar palabra completa (no como substring)
            pattern = r'\b' + re.escape(palabra_obj.palabra.lower()) + r'\b'
            if re.search(pattern, text_lower):
                return True

        return False

    def _analyze_toxicity(self, text: str) -> float:
        """analizar toxicidad del texto usando modelo ml returns: float: score de toxicidad (0.0 - 1.0)"""
        if not self.model:
            return 0.0

        try:
            results = self.model.predict(text)

            #detoxify devuelve múltiples categorias
            #toxicity, severe_toxicity, obscene, threat, insult, identity_attack
            #usamos el máximo score de todas las categorias
            max_score = max([
                results.get('toxicity', 0),
                results.get('severe_toxicity', 0),
                results.get('obscene', 0),
                results.get('threat', 0),
                results.get('insult', 0),
                results.get('identity_attack', 0)
            ])

            return float(max_score)

        except Exception as e:
            print(f"Error en análisis ML: {e}")
            return 0.0

    def _register_infraction(self, id_usuario: int, usuario_nombre: str,
                           mensaje: str, tipo: str, score: float, accion: str):
        """registrar infracción en la base de datos"""
        try:
            InfraccionUsuario.objects.create(
                usuario_id=id_usuario,
                usuario_nombre=usuario_nombre,
                mensaje_original=mensaje,
                tipo_infraccion=tipo,
                score_toxicidad=score,
                accion_tomada=accion
            )
        except Exception as e:
            print(f"Error al registrar infracción: {e}")

    def _should_auto_block(self, id_usuario: int, config: ContentFilterConfig) -> bool:
        """verificar si el usuario debe ser bloqueado automáticamente por acumular demasiadas infracciones"""
        infracciones_count = InfraccionUsuario.objects.filter(
            usuario_id=id_usuario
        ).count()

        if infracciones_count >= config.strikes_para_bloqueo:
            #bloquear usuario automáticamente
            try:
                from django.conf import settings
                from django.apps import apps
                UserModel = apps.get_model(settings.AUTH_USER_MODEL)
                user = UserModel.objects.get(id=id_usuario)
                user.chat_bloqueado = True
                user.save()
                return True
            except Exception as e:
                print(f"Error al bloquear usuario automáticamente: {e}")
                return False

        return False


#instancia global del analizador
content_analyzer = ContentAnalyzer()
