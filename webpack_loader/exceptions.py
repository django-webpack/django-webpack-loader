__all__ = (
    'WebpackError',
    'WebpackLoaderBadStatsError',
    'WebpackLoaderTimeoutError',
    'WebpackBundleLookupError'
)


class WebpackError(Exception):
    """
    General webpack loader error
    """


class WebpackLoaderBadStatsError(WebpackError):
    """
    The stats file does not contain valid data.
    """


class WebpackLoaderTimeoutError(WebpackError):
    """
    The bundle took too long to compile
    """


class WebpackBundleLookupError(WebpackError):
    """
    The bundle name was invalid
    """