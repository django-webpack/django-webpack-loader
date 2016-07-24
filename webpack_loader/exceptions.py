__all__ = ('WebpackError', 'WebpackLoaderBadStatsError')


class WebpackError(Exception):
    pass


class WebpackLoaderBadStatsError(Exception):
    pass


class WebpackLoaderTimeoutError(Exception):
    pass
