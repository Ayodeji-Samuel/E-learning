from django.apps import AppConfig


class EdupathcareConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'eduPathCare'
    
    def ready(self):
        # Import and connect the signals
        import eduPathCare.signals