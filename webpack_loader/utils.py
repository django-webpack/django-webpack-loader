from django.conf import settings
from django.utils.module_loading import import_string

from .config import load_config

_loaders = {}


def get_loader(config_name):
    if config_name not in _loaders:
        config = load_config(config_name)
        loader_class = import_string(config["LOADER_CLASS"])
        _loaders[config_name] = loader_class(config_name, config)
    return _loaders[config_name]


def _filter_by_extension(bundle, extension):
    """Return only files with the given extension"""
    for chunk in bundle:
        if chunk["name"].endswith(f".{extension}"):
            yield chunk


def _get_bundle(loader, bundle_name, extension):
    bundle = loader.get_bundle(bundle_name)
    if extension:
        bundle = _filter_by_extension(bundle, extension)
    return bundle


def get_files(bundle_name, extension=None, config="DEFAULT"):
    """Returns list of chunks from named bundle"""
    return list(_get_bundle(bundle_name, extension, config))


def _render_tags(iterable, attrs="", suffix="", is_preload=False):
    tags = []
    for chunk in iterable:
        if chunk["name"].endswith((".js", ".js.gz")):
            tag = (
                '<link rel="preload" as="script" href="{}" {}/>'
                if is_preload
                else '<script type="text/javascript" src="{}" {}></script>'
            ).format(chunk["url"] + suffix, attrs)
        elif chunk["name"].endswith((".css", ".css.gz")):
            tag = ('<link type="text/css" href="{}" rel={} {}/>').format(
                chunk["url"] + suffix, '"preload" as="style"' if is_preload else '"stylesheet"', attrs
            )
        else:
            continue
        tags.append(tag)
    return tags


def get_as_tags(bundle_name, extension=None, config="DEFAULT", attrs="", suffix="", is_preload=False):
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
    return _render_tags(bundle, attrs, suffix=suffix, is_preload=is_preload)


def _get_entrypoint_files(entrypoint_name, extension, config):
    bundle = get_loader(config).get_entry(entrypoint_name)
    if extension:
        bundle = _filter_by_extension(bundle, extension)
    return bundle


def get_entrypoint_files_as_tags(entrypoint_name, extension=None, config="DEFAULT", attrs=""):
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
    return "{}{}".format(get_loader(config).get_assets().get("publicPath", getattr(settings, "STATIC_URL")), asset_name)


def get_unique_entrypoint_files(entrypoints, extension, config):
    files = list(_get_entrypoint_files(entrypoints[0], extension, config=config))
    for ep in entrypoints[1:]:
        files += [file for file in _get_entrypoint_files(ep, extension, config=config) if file not in files]
    return files
