from setuptools import setup

version = '0.2.4'

setup(
  name = 'django-webpack-loader',
  packages = ['webpack_loader', 'webpack_loader/templatetags', 'webpack_loader/contrib'],
  version = version,
  description = 'Transparently use webpack with django',
  author = 'Owais Lone',
  author_email = 'hello@owaislone.org',
  download_url = 'https://github.com/owais/django-webpack-loader/tarball/{0}'.format(version),
  url = 'https://github.com/owais/django-webpack-loader', # use the URL to the github repo
  keywords = ['django', 'webpack', 'assets'], # arbitrary keywords
  data_files = [("", ["LICENSE"])],
  classifiers = [
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
    'Framework :: Django',
    'Environment :: Web Environment',
    'License :: OSI Approved :: MIT License',
  ],
)
