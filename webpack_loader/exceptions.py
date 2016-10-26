__all__ = (
    'WebpackError',
    'WebpackLoaderBadStatsError',
    'WebpackLoaderTimeoutError',
    'WebpackBundleLookupError'
)


class WebpackError(Exception):
    pass


class WebpackLoaderBadStatsError(Exception):
    pass


class WebpackLoaderTimeoutError(Exception):
    pass


class WebpackBundleLookupError(Exception):
    pass
