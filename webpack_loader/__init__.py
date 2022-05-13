__author__ = "Owais Lone"
__version__ = "0.8.5"

import django

if django.VERSION < (3, 2):  # pragma: no cover
    default_app_config = "webpack_loader.apps.WebpackLoaderConfig"
