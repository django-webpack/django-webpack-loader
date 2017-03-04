import os
import re

from setuptools import setup


def rel(*parts):
    '''returns the relative path to a file wrt to the current directory'''
    return os.path.abspath(os.path.join(os.path.dirname(__file__), *parts))

if os.path.isfile('README.rst'):
  README = open('README.rst', 'r').read()
else:
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
  author = 'Owais Lone',
  author_email = 'hello@owaislone.org',
  download_url = 'https://github.com/owais/django-webpack-loader/tarball/{0}'.format(VERSION),
  url = 'https://github.com/owais/django-webpack-loader', # use the URL to the github repo
  keywords = ['django', 'webpack', 'assets'], # arbitrary keywords
  classifiers = [
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Framework :: Django',
    'Environment :: Web Environment',
    'License :: OSI Approved :: MIT License',
  ],
)
