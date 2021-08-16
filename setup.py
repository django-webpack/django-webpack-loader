import os
import re

from setuptools import setup


def rel(*parts):
    '''returns the relative path to a file wrt to the current directory'''
    return os.path.abspath(os.path.join(os.path.dirname(__file__), *parts))

README = open('README.md', 'r').read()

with open(rel('webpack_loader', '__init__.py')) as handler:
    INIT_PY = handler.read()


VERSION = re.findall("__version__ = '([^']+)'", INIT_PY)[0]

setup(
  name = 'django-webpack-loader',
  packages = ['webpack_loader', 'webpack_loader/templatetags', 'webpack_loader/contrib'],
  version = VERSION,
  description = 'Transparently use webpack with django',
  long_description=README,
  long_description_content_type="text/markdown",
  author = 'Owais Lone',
  author_email = 'hello@owaislone.org',
  download_url = 'https://github.com/django-webpack/django-webpack-loader/tarball/{0}'.format(VERSION),
  url = 'https://github.com/django-webpack/django-webpack-loader', # use the URL to the github repo
  keywords = ['django', 'webpack', 'assets'], # arbitrary keywords
  classifiers = [
    'Programming Language :: Python',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Framework :: Django',
    'Framework :: Django :: 2.0',
    'Framework :: Django :: 2.1',
    'Framework :: Django :: 2.2',
    'Framework :: Django :: 3.0',
    'Framework :: Django :: 3.1',
    'Framework :: Django :: 3.2',
    'Environment :: Web Environment',
    'License :: OSI Approved :: MIT License',
  ],
)
