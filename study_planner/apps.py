from django.apps import AppConfig


class StudyPlannerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'study_planner'

    def ready(self):
        # Import signals when the app is ready
        import study_planner.signals  # Replace with the correct path to your signals module