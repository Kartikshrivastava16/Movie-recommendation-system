from django.apps import AppConfig


class RecommenderAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'recommender_app'

    def ready(self):
        # Only initialize when actually serving (not during migrate, collectstatic, etc.)
        import sys
        if 'runserver' in sys.argv or 'gunicorn' in sys.argv[0]:
            from recommender_app import ml_engine
            ml_engine.initialize()
        else:
            # Still initialize for any command that needs it
            try:
                from recommender_app import ml_engine
                ml_engine.initialize()
            except Exception:
                pass
