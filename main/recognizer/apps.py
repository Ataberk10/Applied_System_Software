from django.apps import AppConfig
import sys


class RecognizerConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "recognizer"

    def ready(self):
        # This method is called when Django starts.
        # Avoid initialization during `manage.py makemigrations` or `manage.py migrate`
        # as models might not be fully loaded or database might not be ready.
        # Also, `runserver` often runs twice (once for stat reloader).
        is_manage_py = any(arg.casefold().endswith("manage.py") for arg in sys.argv)
        is_runserver = "runserver" in sys.argv

        if (
            is_manage_py and is_runserver
        ) or not is_manage_py:  # More robust check for server startup
            # Check if we are in the main process for runserver (to avoid initializing twice due to reloader)
            import os

            if (
                os.environ.get("RUN_MAIN") == "true" or not is_runserver
            ):  # RUN_MAIN is set by Django's reloader
                print("RecognizerConfig.ready(): Initializing services...")
                from . import face_analyzer

                try:
                    face_analyzer.initialize_face_analyzer()
                    print("Face analyzer initialized successfully from apps.py.")
                except Exception as e:
                    print(f"Failed to initialize face analyzer in apps.py: {e}")
            elif is_runserver:
                print(
                    "RecognizerConfig.ready(): In reloader process, skipping initialization here."
                )
