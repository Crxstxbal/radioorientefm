from django.apps import AppConfig


class ContactConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.contact'
    verbose_name = 'Contacto'

    def ready(self):
        """importar señales cuando la aplicación esté lista"""
        import apps.contact.signals  # noqa
