from django.apps import AppConfig


class ArticulosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.articulos'
    verbose_name = 'Artículos'

    def ready(self):
        """Importar señales cuando la aplicación esté lista"""
        import apps.articulos.signals  # noqa
