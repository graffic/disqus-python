"""Cursor and other goodies for DisquisAPI methods"""
from disqusapi import Result
from disqusapi.exceptions import RateLimitError


class Paginator(object):
    """
    Paginate through all entries:

    >>> from disqusapi.paginator import Paginator
    >>> from disqusapi import DisqusAPI
    >>> api = DisqusAPI('secret_key')
    >>> paginator = Paginator(api.trends.listThreads, forum='disqus')
    >>> for result in paginator:
    >>>     print(result)

    Paginate only up to a number of entries:

    >>> for result in paginator(limit=500):
    >>>     print(result)

    Paginate till you run out of api calls:

    >>> for result in paginator(silence_limit=True):
    >>>     print(result)
    """

    def __init__(self, endpoint, **params):
        self.endpoint = endpoint
        self.params = params

    def __iter__(self):
        for result in self():
            yield result

    def __call__(self, limit=None, silence_limit=False):
        endpoint = self.endpoint
        if silence_limit:
            endpoint = ignore_limit(endpoint)
        endpoint = use_cursor(endpoint)
        if limit is not None:
            endpoint = limit_amount(endpoint, limit)
        for result in endpoint(**self.params):
            yield result


def limit_amount(endpoint, limit):
    def wrapped(**kwargs):
        count = 0
        for result in endpoint(**kwargs):
            yield result
            count += 1
            if limit == count:
                break
    return wrapped


def use_cursor(endpoint):
    def wrapped(**kwargs):
        while True:
            results = endpoint(**kwargs)
            for result in results:
                yield result

            if results.cursor and results.cursor['more']:
                kwargs['cursor'] = results.cursor['id']
            else:
                break
    return wrapped


def ignore_limit(endpoint):
    def wrapped(**kwargs):
        try:
            return endpoint(**kwargs)
        except RateLimitError:
            return Result([])
    return wrapped
