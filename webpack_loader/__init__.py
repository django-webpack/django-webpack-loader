__author__ = "Vinta Software"
__version__ = "3.0.1"

import django

if django.VERSION < (3, 2):  # pragma: no cover
    default_app_config = "webpack_loader.apps.WebpackLoaderConfig"
