from django.apps import AppConfig


class RatingSystemConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'rating_system'

    def ready(self):
        # Импортируем сигналы при запуске приложения
        import rating_system.signals
