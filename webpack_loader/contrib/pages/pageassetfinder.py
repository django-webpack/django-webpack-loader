import os
import urllib.parse

from django.apps import apps
from django.conf import settings
from django.contrib.staticfiles import finders, utils

from webpack_loader.config import load_config


class PageAssetFinder(finders.BaseFinder):
    def __init__(self, *args, config="DEFAULT", **kwargs):
        super(PageAssetFinder, self).__init__(*args, **kwargs)
        self.pageassets = {}  # pagename: storage instance
        config = load_config(config)
        self.load_pages(config["ROOT_PAGE_DIR"], namespace="root")
        for app_config in apps.get_app_configs():
            self.load_pages(os.path.join(app_config.path, ""), namespace=app_config.name)

    def load_pages(self, path, namespace=None):
        if not os.path.exists(path):
            return
        for pagepath in os.listdir(path):
            if os.path.isdir(os.path.join(path, pagepath)) and pagepath != "assets":
                pagename = f"{namespace}.{pagepath}" if namespace else pagepath
                if os.path.exists(os.path.join(path, pagepath, "assets")):
                    self.pageassets[pagename] = finders.FileSystemStorage(os.path.join(path, pagepath, "assets"))
                    self.pageassets[pagename].prefix = self.page_asset_name(pagename, "")
                self.load_pages(os.path.join(path, pagepath), namespace=pagename)

    def check(self, **kwargs):
        errors = []
        return errors

    def list(self, ignore_patterns):
        for pagename, assetstorage in self.pageassets.items():
            if assetstorage.exists(""):
                for path in utils.get_files(assetstorage, ignore_patterns):
                    yield path, assetstorage

    # noinspection PyShadowingBuiltins
    def find(self, path, all=False):
        pathelements = os.path.normpath(path).split(os.path.sep)
        if pathelements[0] == "assets":
            assets = self.pageassets.get(pathelements[1])
            if assets and assets.exists(os.path.join(*pathelements[2:])):
                matched_path = assets.path(os.path.join(*pathelements[2:]))
                if matched_path and not all:
                    return matched_path
                elif matched_path and all:
                    return [matched_path]
        return []

    @staticmethod
    def page_asset_name(pagename, path):
        return os.path.join("assets", pagename, path)

    @staticmethod
    def page_asset_url(pagename, path):
        return urllib.parse.urljoin(settings.STATIC_URL, PageAssetFinder.page_asset_name(pagename, path))
