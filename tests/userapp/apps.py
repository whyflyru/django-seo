from django.apps.config import AppConfig

from djangoseo.models import setup


class UserAppConfig(AppConfig):
    name = 'userapp'

    def ready(self):
        setup()
