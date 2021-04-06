# django-webpack5-loader

[![PyPI version](https://badge.fury.io/py/django-webpack5-loader.svg)](https://badge.fury.io/py/django-webpack5-loader)
[![Build Status](https://circleci.com/gh/MrP01/django-webpack-loader/tree/master.svg?style=svg)](https://circleci.com/gh/owais/django-webpack-loader/tree/master)
[![Coverage Status](https://coveralls.io/repos/MrP01/django-webpack-loader/badge.svg?branch=master&service=github)](https://coveralls.io/github/owais/django-webpack-loader?branch=master)
[![Join the chat at https://gitter.im/owais/django-webpack-loader](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/owais/django-webpack-loader?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

Read http://owaislone.org/blog/webpack-plus-reactjs-and-django/ for a detailed step-by-step guide on setting up webpack
with django using this library.

Use webpack to generate your static bundles without django's staticfiles or opaque wrappers.

Django webpack loader consumes the output generated
by [webpack-bundle-tracker](https://github.com/owais/webpack-bundle-tracker) and lets you use the generated bundles in
django. **If you want to use entrypoints**, please use [webpack4-bundle-tracker](https://www.npmjs.com/package/webpack4-bundle-tracker).

If you want to leverage webpack critical css generation while maintaining
a Django-like structure in your project, have a look at [webpack-critical-pages](https://www.npmjs.com/package/webpack-critical-pages).

A [changelog](CHANGELOG.md) is also available.

## Purpose of this Fork

This package aims not only to support webpack 4 and 5, introduce additional loading of entrypoints in templates,
but also adds a framework for structuring django projects into pages using `webpack_loader.contrib.pages`.
See below.

The [initial webpack 4 port](https://github.com/alihazemfarouk/django-webpack-loader) was made possible thanks to

- Svetoslav Dekov
- Ali Farouk
- Nikolaus Piccolotto

apart from the
[original package](https://github.com/owais/django-webpack-loader) author
[Owais Lone](https://github.com/owais).

## Usage

### Manually run webpack to build assets.

One of the core principles of django-webpack-loader is to not manage webpack itself in order to give you the flexibility
to run webpack the way you want. If you are new to webpack, check one of
the [examples](https://github.com/owais/django-webpack-loader/tree/master/examples),
read [my detailed blog post](http://owaislone.org/blog/webpack-plus-reactjs-and-django/) or
check [webpack docs](http://webpack.github.io/).

### Settings

Add `webpack_loader` to `INSTALLED_APPS`

```
INSTALLED_APPS = (
    ...
    'webpack_loader',
)
```

### Templates

#### render_bundle

```HTML+Django
{% load render_bundle from webpack_loader %}

{% render_bundle 'main' %}
```

`render_bundle` will render the proper `<script>` and `<link>` tags needed in your template.

`render_bundle` also takes a second argument which can be a file extension to match. This is useful when you want to
render different types for files in separately. For example, to render CSS in head and JS at bottom we can do something
like this,

```HTML+Django
{% load render_bundle from webpack_loader %}

<html>
  <head>
    {% render_bundle 'main' 'css' %}
  </head>
  <body>
    ....
    {% render_bundle 'main' 'js' %}
  </body>
</head>
```

#### render_entrypoint (Available only when using Webpack v.4 or newer)

```HTML+Django
{% load render_entrypoint from webpack_loader %}

{% render_entrypoint 'index' %}
```

`render_entrypoint` will render all the proper `<script>` and `<link>` tags needed in your template for that endpoint.
Using this, you can make use of webpack 4 code splitting features. Example webpack config:

```javascript
module.exports = {
  ...,
  entry: {
    index: "./myapp/static/src/pages/index.js",
    contact_us: "./myapp/static/src/pages/contact_us.js",
  },
  ...,
  plugins: [new BundleTracker({filename: "./webpack-stats.json"})]
};

```

Just as `render_bundle`, `render_entrypoint` also takes a second argument which can be a file extension to match, and
can be used in a similar way,

```HTML+Django
{% load render_entrypoint from webpack_loader %}

<html>
  <head>
    {% render_entrypoint 'main' 'css' %}
  </head>
  <body>
    ....
    {% render_entrypoint 'main' 'js' %}
  </body>
</head>
```

### Automatic page handling based on Entrypoints

Using `webpack_loader.contrib.pages` you can register entrypoints for corresponding pages in templates.

At the top of your individual page, do:
```HTML+Jinja
{% extends "layout.jinja" %}
{% do register_entrypoint("myapp/dashboard") %}
```

In the layout's (base template's) head, place the following:
```HTML+Jinja
<!DOCTYPE html>
{% do register_entrypoint("main") %}
<html lang="{{ LANGUAGE_CODE }}">
<head>
  ...
  {{ render_css() }}
</head>
<body>
  ...
  {{ render_js() }}
</body>
```

This will load the registered entrypoints in order (`main`, then `myapp/dashboard`) and automatically inject
the webpack-generated css and js. It also supports critical css injection upon first request visits.

### Multiple webpack projects

Version 2.0 and up of webpack loader also supports multiple webpack configurations. The following configuration defines
2 webpack stats files in settings and uses the `config` argument in the template tags to influence which stats file to
load the bundles from.

```python
WEBPACK_LOADER = {
    'DEFAULT': {
        'BUNDLE_DIR_NAME': 'bundles/',
        'STATS_FILE': os.path.join(BASE_DIR, 'webpack-stats.json'),
    },
    'DASHBOARD': {
        'BUNDLE_DIR_NAME': 'dashboard_bundles/',
        'STATS_FILE': os.path.join(BASE_DIR, 'webpack-stats-dashboard.json'),
    }
}
```

```HTML+Django
{% load render_bundle from webpack_loader %}

<html>
  <body>
    ....
    {% render_bundle 'main' 'js' 'DEFAULT' %}
    {% render_bundle 'main' 'js' 'DASHBOARD' %}

    <!-- or render all files from a bundle -->
    {% render_bundle 'main' config='DASHBOARD' %}

    <!-- the following tags do the same thing -->
    {% render_bundle 'main' 'css' 'DASHBOARD' %}
    {% render_bundle 'main' extension='css' config='DASHBOARD' %}
    {% render_bundle 'main' config='DASHBOARD' extension='css' %}

    <!-- add some extra attributes to the tag -->
    {% render_bundle 'main' 'js' 'DEFAULT' attrs='async charset="UTF-8"'%}
  </body>
</head>
```

### File URLs instead of html tags

If you need the URL to an asset without the HTML tags, the `get_files`
template tag can be used. A common use case is specifying the URL to a custom css file for a Javascript plugin.

`get_files` works exactly like `render_bundle` except it returns a list of matching files and lets you assign the list
to a custom template variable. For example,

```HTML+Django
{% get_files 'editor' 'css' as editor_css_files %}
CKEDITOR.config.contentsCss = '{{ editor_css_files.0.publicPath }}';

<!-- or list down name, path and download url for every file -->
<ul>
{% for css_file in editor_css_files %}
    <li>{{ css_file.name }} : {{ css_file.path }} : {{ css_file.publicPath }}</li>
{% endfor %}
</ul>
```

### Refer other static assets

`webpack_static` template tag provides facilities to load static assets managed by webpack in django templates. It is
like django's built in `static` tag but for webpack assets instead.

In the below example, `logo.png` can be any static asset shipped with any npm or bower package.

```HTML+Django
{% load webpack_static from webpack_loader %}

<!-- render full public path of logo.png -->
<img src="{% webpack_static 'logo.png' %}"/>
```

The public path is based
on `webpack.config.js` [output.publicPath](https://webpack.js.org/configuration/output/#output-publicpath).

### From Python code

If you want to access the webpack asset path information from your application code then you can use the function in
the `webpack_loader.utils` module.

```python
>>> utils.get_files('main')
[{'url': '/static/bundles/main.js',
  u'path': u'/home/mike/root/projects/django-webpack-loader/tests/assets/bundles/main.js', u'name': u'main.js'},
 {'url': '/static/bundles/styles.css',
  u'path': u'/home/mike/root/projects/django-webpack-loader/tests/assets/bundles/styles.css', u'name': u'styles.css'}]
>>> utils.get_as_tags('main')
['<script type="text/javascript" src="/static/bundles/main.js" ></script>',
 '<link type="text/css" href="/static/bundles/styles.css" rel="stylesheet" />']
```

## Compatibility

Test cases cover Django>=1.6 on Python 2.7 and Python>=3.4. 100% code coverage is the target, so we can be sure
everything works anytime. It should probably work on older version of django as well, but the package does not ship any
test cases for them.

## Install

```bash
npm install --save-dev webpack-bundle-tracker

pip install django-webpack-loader
```

## Configuration

### Assumptions

Assuming `BASE_DIR` in settings refers to the root of your django app.

```python
import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
```

Assuming `assets/` is in `settings.STATICFILES_DIRS` like

```python
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'assets'),
)
```

Assuming your webpack config lives at `./webpack.config.js` and looks like this

```javascript
var path = require('path');
var webpack = require('webpack');
var BundleTracker = require('webpack-bundle-tracker');

module.exports = {
  context: __dirname,
  entry: './assets/js/index',
  output: {
    path: path.resolve('./assets/webpack_bundles/'),
    filename: "[name]-[hash].js"
  },

  plugins: [
    new BundleTracker({filename: './webpack-stats.json'})
  ]
}
```

### Default Configuration

```python
WEBPACK_LOADER = {
    'DEFAULT': {
        'CACHE': not DEBUG,
        'BUNDLE_DIR_NAME': 'webpack_bundles/',  # must end with slash
        'STATS_FILE': os.path.join(BASE_DIR, 'webpack-stats.json'),
        'POLL_INTERVAL': 0.1,
        'TIMEOUT': None,
        'IGNORE': [r'.+\.hot-update.js', r'.+\.map'],
        'LOADER_CLASS': 'webpack_loader.loader.WebpackLoader',
        'EXCLUDE_RUNTIME': False,
        'BASE_ENTRYPOINT': ''
    }
}
```

#### CACHE

```python
WEBPACK_LOADER = {
    'DEFAULT': {
        'CACHE': not DEBUG
    }
}
```

When `CACHE` is set to True, webpack-loader will read the stats file only once and cache the result. This means web
workers need to be restarted in order to pick up any changes made to the stats files.

#### BUNDLE_DIR_NAME

```python
WEBPACK_LOADER = {
    'DEFAULT': {
        'BUNDLE_DIR_NAME': 'bundles/'  # end with slash
    }
}
```

`BUNDLE_DIR_NAME` refers to the dir in which webpack outputs the bundles. It should not be the full path. If `./assets`
is one of your static dirs and webpack generates the bundles in `./assets/output/bundles/`, then `BUNDLE_DIR_NAME`
should be `output/bundles/`.

If the bundle generates a file called `main-cf4b5fab6e00a404e0c7.js` and your STATIC_URL is `/static/`, then
the `<script>` tag will look like this

```html

<script type="text/javascript" src="/static/output/bundles/main-cf4b5fab6e00a404e0c7.js"/>
```

**NOTE:** If your webpack config outputs the bundles at the root of your `staticfiles` dir, then `BUNDLE_DIR_NAME`
should be an empty string `''`, not `'/'`.

#### STATS_FILE

```python
WEBPACK_LOADER = {
    'DEFAULT': {
        'STATS_FILE': os.path.join(BASE_DIR, 'webpack-stats.json')
    }
}
```

`STATS_FILE` is the filesystem path to the file generated by `webpack-bundle-tracker` plugin. If you
initialize `webpack-bundle-tracker` plugin like this

```javascript
new BundleTracker({filename: './webpack-stats.json'})
```

and your webpack config is located at `/home/src/webpack.config.js`, then the value of `STATS_FILE` should
be `/home/src/webpack-stats.json`

#### IGNORE

`IGNORE` is a list of regular expressions. If a file generated by webpack matches one of the expressions, the file will
not be included in the template.

#### POLL_INTERVAL

`POLL_INTERVAL` is the number of seconds webpack_loader should wait between polling the stats file. The stats file is
polled every 100 miliseconds by default and any requests to are blocked while webpack compiles the bundles. You can
reduce this if your bundles take shorter to compile.

**NOTE:** Stats file is not polled when in production (DEBUG=False).

#### TIMEOUT

`TIMEOUT` is the number of seconds webpack_loader should wait for webpack to finish compiling before raising an
exception. `0`, `None` or leaving the value out of settings disables timeouts.

#### LOADER_CLASS

`LOADER_CLASS` is the fully qualified name of a python class as a string that holds the custom webpack loader. This is
where behavior can be customized as to how the stats file is loaded. Examples include loading the stats file from a
database, cache, external url, etc. For convenience, `webpack_loader.loader.WebpackLoader` can be extended;
The `load_assets` method is likely where custom behavior will be added. This should return the stats file as an object.

Here's a simple example of loading from an external url:

```py
# in app.module
import requests
from webpack_loader.loader import WebpackLoader


class ExternalWebpackLoader(WebpackLoader):

    def load_assets(self):
        url = self.config['STATS_URL']
        return requests.get(url).json()


# in app.settings
WEBPACK_LOADER = {
    'DEFAULT': {
        'CACHE': False,
        'BUNDLE_DIR_NAME': 'bundles/',
        'LOADER_CLASS': 'app.module.ExternalWebpackLoader',
        # Custom config setting made available in WebpackLoader's self.config
        'STATS_URL': 'https://www.test.com/path/to/stats/',
    }
}
```

#### EXCLUDE_RUNTIME

`EXCLUDE_RUNTIME` is meant to be used with `render_entrypoint`. When creating multi-page applications, it's common to
want to split a single runtime file that is used by all chunks. You can do that by using `{% render_bundle 'runtime' %}`
in your base HTML file and setting `EXCLUDE_RUNTIME` to `True` in order to not include it again when
using `{% render_entrypoint 'example_entry_point' %}`

#### BASE_ENTRYPOINT

`BASE_ENTRYPOINT` is meant to be used with `render_entrypoint`. When creating multi-page applications, it's common to
want to include common js in the base HTML. If the main entrypoint's name is `main`, you can do that by
including `{% render_entrypoint 'main' %}` in your base HTML file. Now in another entrypoints (that extend the base HTML
file), there might be some chunks that were already included in `main`, that means they would be included twice in the
final rendered HTML, to avoid that, set `BASE_ENTRYPOINT` to `'main'`, then any duplicate chunks between an entrypoint
and the main entrypoint would be included only once.

## How to use in Production

**It is up to you**. There are a few ways to handle this. I like to have slightly separate configs for production and
local. I tell git to ignore my local stats + bundle file but track the ones for production. Before pushing out newer
version to production, I generate a new bundle using production config and commit the new stats file and bundle. I store
the stats file and bundles in a directory that is added to the `STATICFILES_DIR`. This gives me integration with
collectstatic for free. The generated bundles are automatically collected to the target directory and synched to S3.

`./webpack_production.config.js`

```javascript
var config = require('./webpack.config.js');
var BundleTracker = require('webpack-bundle-tracker');

config.output.path = require('path').resolve('./assets/dist');

config.plugins = [
  new BundleTracker({filename: './webpack-stats-prod.json'})
]

// override any other settings here like using Uglify or other things that make sense for production environments.

module.exports = config;
```

`settings.py`

```python
if not DEBUG:
    WEBPACK_LOADER.update({
        'BUNDLE_DIR_NAME': 'dist/',
        'STATS_FILE': os.path.join(BASE_DIR, 'webpack-stats-prod.json')
    })
```

You can also simply generate the bundles on the server before running collectstatic if that works for you.

## Extra

### Jinja2 Configuration

If you need to output your assets in a jinja template we provide a Jinja2 extension that's compatible with
the [Django Jinja](https://github.com/niwinz/django-jinja) module and Django 1.8.

To install the extension add it to the django_jinja `TEMPLATES` configuration in the `["OPTIONS"]["extension"]` list.

```python
TEMPLATES = [
    {
        "BACKEND": "django_jinja.backend.Jinja2",
        "OPTIONS": {
            "extensions": [
                "django_jinja.builtins.extensions.DjangoFiltersExtension",
                "webpack_loader.contrib.jinja2ext.WebpackExtension",
            ],
        }
    }
]
```

Then in your base jinja template:

```HTML
{{ render_bundle('main') }}
```

--------------------

Enjoy your webpack with django :)

# Alternatives to Django-Webpack-Loader

_Below are known projects that attempt to solve the same problem:_

Note that these projects have not been vetted or reviewed in any way by me.
These are not recommendation.
Anyone can add their project to this by sending a PR.

* [Django Manifest Loader](https://github.com/shonin/django-manifest-loader)
* [Python Webpack Boilerplate](https://github.com/AccordBox/python-webpack-boilerplate)
