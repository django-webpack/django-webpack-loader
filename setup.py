from distutils.core import setup
setup(
  name = 'django-webpack-loader',
  packages = ['webpack_loader', 'webpack_loader/templatetags'], # this must be the same as the name above
  version = '0.0.7',
  description = 'Load your webpack bundles and chunks in django',
  author = 'Owais Lone',
  author_email = 'hello@owaislone.org',
  download_url = 'https://github.com/owais/django-webpack-loader/tarball/0.0.3',
  url = 'https://github.com/owais/django-webpack-loader', # use the URL to the github repo
  keywords = ['django', 'webpack', 'assets'], # arbitrary keywords
  data_files = [("", ["LICENSE"])],
  classifiers = [
    'Programming Language :: Python :: 2.7',
    'Framework :: Django',
    'Environment :: Web Environment',
    'License :: OSI Approved :: MIT License',
  ],
)
