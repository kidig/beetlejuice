from django.apps import AppConfig

class ProjectNameAppConfig(AppConfig):
    name = 'project_name'

    def ready(self):
        # noinspection PyUnresolvedReferences
        from . import receivers
