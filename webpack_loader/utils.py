from .loader import WebpackLoader


_loaders = {}


def get_loader(config_name):
    if config_name not in _loaders:
        _loaders[config_name] = WebpackLoader(config_name)
    return _loaders[config_name]
