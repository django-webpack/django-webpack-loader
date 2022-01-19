__author__ = 'Owais Lone'
__version__ = '1.4.1'

import django

if django.VERSION < (3, 2):  # pragma: no cover
    default_app_config = 'webpack_loader.apps.WebpackLoaderConfig'
