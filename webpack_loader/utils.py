from django.conf import settings
from django.utils import translation
from django.utils.module_loading import import_string

from .config import load_config

_loaders = {}


def get_loader(config_name):
    config = load_config(config_name)

    loader_name = config_name
    locale = None
    if config["LOCALIZED_BUILDS"]:
        locale = translation.get_language()
        loader_name += "-" + locale

    if loader_name not in _loaders:
        loader_class = import_string(config["LOADER_CLASS"])
        _loaders[loader_name] = loader_class(loader_name, config, locale)
    return _loaders[loader_name]


def _filter_by_extension(bundle, extension):
    """Return only files with the given extension"""
    for chunk in bundle:
        if chunk["name"].endswith(".{0}".format(extension)):
            yield chunk


def _get_bundle(bundle_name, extension, config):
    bundle = get_loader(config).get_bundle(bundle_name)
    if extension:
        bundle = _filter_by_extension(bundle, extension)
    return bundle


def get_files(bundle_name, extension=None, config="DEFAULT"):
    """Returns list of chunks from named bundle"""
    return list(_get_bundle(bundle_name, extension, config))


def _render_tags(iterable, attrs=""):
    tags = []
    for chunk in iterable:
        if chunk["name"].endswith((".js", ".js.gz")):
            tags.append((
                '<script type="text/javascript" src="{0}" {1}></script>'
            ).format(chunk["url"], attrs))
        elif chunk["name"].endswith((".css", ".css.gz")):
            tags.append((
                '<link type="text/css" href="{0}" rel="stylesheet" {1}/>'
            ).format(chunk["url"], attrs))
    return tags


def get_as_tags(bundle_name, extension=None, config="DEFAULT", attrs=""):
    """
    Get a list of formatted <script> & <link> tags for the assets in the
    named bundle.

    :param bundle_name: The name of the bundle
    :param extension: (optional) filter by extension, eg. "js" or "css"
    :param config: (optional) the name of the configuration
    :param attrs: (optional) further attributes on the tags
    :return: a list of formatted tags as strings
    """
    bundle = _get_bundle(bundle_name, extension, config)
    return _render_tags(bundle, attrs)


def _get_entrypoint_files(entrypoint_name, extension, config):
    bundle = get_loader(config).get_entry(entrypoint_name)
    if extension:
        bundle = _filter_by_extension(bundle, extension)
    return bundle


def get_entrypoint_files_as_tags(entrypoint_name, extension=None, config="DEFAULT", attrs=''):
    """
    Get a list of formatted <script> & <link> tags for the assets required by a
    particular endpoint.

    :param entrypoint_name: The name of the entrypoint
    :param extension: (optional) filter by extension, eg. 'js' or 'css'
    :param config: (optional) the name of the configuration
    :param attrs: (optional) further attributes on the tags
    :return: a list of formatted tags as strings
    """
    entrypoint_files = _get_entrypoint_files(entrypoint_name, extension, config)
    return _render_tags(entrypoint_files, attrs)


def get_static(asset_name, config="DEFAULT"):
    """
    Equivalent to Django's "static" look up but for webpack assets.

    :param asset_name: the name of the asset
    :param config: (optional) the name of the configuration
    :return: path to webpack asset as a string
    """
    return "{0}{1}".format(
        get_loader(config).get_assets().get(
            "publicPath", getattr(settings, "STATIC_URL")
        ),
        asset_name
    )


def get_unique_entrypoint_files(entrypoints, extension, config):
    files = list(_get_entrypoint_files(entrypoints[0], extension, config=config))
    for ep in entrypoints[1:]:
        files += [file for file in _get_entrypoint_files(ep, extension, config=config) if file not in files]
    return files
