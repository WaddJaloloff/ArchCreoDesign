# app/apps.py

from django.apps import AppConfig
import threading
import os

class AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'

    def ready(self):
        # Django autoreload tufayli ikki marta ishga tushmasligi uchun
        if os.environ.get('RUN_MAIN') != 'true':
            return

        from bot import server_bot
        threading.Thread(target=server_bot.run_bot, daemon=True).start()
