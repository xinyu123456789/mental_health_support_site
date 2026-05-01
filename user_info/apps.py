from django.apps import AppConfig

class UserInfoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'user_info'

    def ready(self):
        # 啟動時載入 signals
        import user_info.signals