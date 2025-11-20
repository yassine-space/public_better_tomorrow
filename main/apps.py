from django.apps import AppConfig

class MainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main'

    def ready(self):
        # Import inside the function to avoid "Apps aren't loaded yet"
        from django.contrib.auth import get_user_model

        User = get_user_model()
        try:
            if not User.objects.filter(username='mohammed').exists():
                User.objects.create_superuser(username='mohammed', password='mohammed', email='')
                print("✅ Default admin user 'mohammed' created.")
        except Exception as e:
            # Avoid errors during migration phase
            print(f"⚠️ Could not create default admin user: {e}")
