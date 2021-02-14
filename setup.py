#!/usr/bin/env python3
import os
import re

from setuptools import setup


def rel(*parts):
    """returns the relative path to a file wrt to the current directory"""
    return os.path.abspath(os.path.join(os.path.dirname(__file__), *parts))


README = open("README.md", "r").read()
with open(rel("webpack_loader", "__init__.py")) as handler:
    INIT_PY = handler.read()
VERSION = re.findall("__version__ = '([^']+)'", INIT_PY)[0]

setup(
    name="django-webpack5-loader",
    packages=[
        "webpack_loader",
        "webpack_loader/templatetags",
        "webpack_loader/contrib",
        "webpack_loader/contrib/pages",
        "webpack_loader/contrib/pages/templatetags",
    ],
    version=VERSION,
    description="Transparently use webpack with django",
    long_description=README,
    long_description_content_type="text/markdown",
    author="Owais Lone",
    author_email="hello@owaislone.org",
    url="https://github.com/MrP01/django-webpack-loader",  # use the URL to the github repo
    keywords=["django", "webpack", "assets"],  # arbitrary keywords
    classifiers=[
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Framework :: Django",
        "Environment :: Web Environment",
        "License :: OSI Approved :: MIT License",
    ],
)
