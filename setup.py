import os
import re

from setuptools import setup


def rel(*parts):
    """returns the relative path to a file wrt to the current directory"""
    return os.path.abspath(os.path.join(os.path.dirname(__file__), *parts))


with open("README.md", "r") as handler:
    README = handler.read()

with open(rel("webpack_loader", "__init__.py")) as handler:
    INIT_PY = handler.read()


VERSION = re.findall(r"__version__ = \"([^\"]+)\"", INIT_PY)[0]

setup(
    name="django-webpack-loader",
    packages=[
        "webpack_loader",
        "webpack_loader/templatetags",
        "webpack_loader/contrib",
    ],
    version=VERSION,
    license="MIT License",
    description="Transparently use webpack with django",
    long_description=README,
    long_description_content_type="text/markdown",
    author="Vinta Software",
    author_email="contact@vinta.com.br",
    download_url="https://github.com/django-webpack/django-webpack-loader/tarball/{0}".format(
        VERSION
    ),
    url="https://github.com/django-webpack/django-webpack-loader",  # use the URL to the github repo
    keywords=["django", "webpack", "assets"],  # arbitrary keywords
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Framework :: Django",
        "Framework :: Django :: 3.2",
        "Framework :: Django :: 4.2",
        "Framework :: Django :: 5.0",
        "Framework :: Django :: 5.1",
        "Environment :: Web Environment",
        "License :: OSI Approved :: MIT License",
    ],
)
