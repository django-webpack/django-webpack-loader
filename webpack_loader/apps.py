from django.apps import AppConfig


class WebpackLoaderConfig(AppConfig):
    name = 'webpack_loader'
    verbose_name = "Webpack Loader"

    def ready(self):
        from . import signals
