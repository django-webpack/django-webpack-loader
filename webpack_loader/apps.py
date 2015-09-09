from django.apps import AppConfig


def webpack_cfg_check(app_configs, **kwargs):
    from django.conf import settings
    from django.core.checks import Error

    check_failed = False
    user_config = getattr(settings, 'WEBPACK_LOADER', {})
    try:
        user_config = [dict({}, **cfg) for cfg in user_config.values()]
    except TypeError:
        check_failed = True

    errors = []
    if check_failed:
        errors.append(
            Error(
                'Error while parsing WEBPACK_LOADER configuration',
                hint='Is WEBPACK_LOADER config compliant with the new format?',
                obj='django.conf.settings.WEBPACK_LOADER',
                id='django-webpack-loader.E001',
            )
        )
    return errors


class WebpackLoaderConfig(AppConfig):
    name = 'webpack_loader'
    verbose_name = "Webpack Loader"

    def ready(self):
        from . import signals
        from django.core.checks import register, Tags
        register(Tags.compatibility)(webpack_cfg_check)
