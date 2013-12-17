"""
disqus-python
~~~~~~~~~~~~~

disqus = DisqusAPI(secret_key)
disqus.trends.listThreads()

"""
try:
    __version__ = __import__('pkg_resources') \
        .get_distribution('disqusapi').version
except:
    __version__ = 'unknown'

import os.path
import simplejson

from disqusapi.compat import urlencode, HTTPSConnection
from disqusapi.exceptions import (
    InterfaceNotDefined,
    APIError,
    InvalidAccessToken,
    RateLimitError)

__all__ = ['DisqusAPI']


class Result(object):
    """
    Wraps a result dictionary and its cursor.

    It allows common operations directly over the response part.
    """
    def __init__(self, response, cursor=None):
        self.response = response
        self.cursor = cursor or {}

    def __repr__(self):
        return '<Result: %s>' % repr(self.response)

    def __iter__(self):
        for result in self.response:
            yield result

    def __len__(self):
        return len(self.response)

    def __getitem__(self, key):
        return self.response.__getitem__(key)

    def __contains__(self, key):
        return self.response.__contains__(key)

    def __eq__(self, other):
        return self.response == other.response and \
            self.cursor == other.cursor


class ResourceElement(object):
    """
    Object like walking resource generation

    This allows resource generation in this form:

    >>> this.is.an.api.resource.now

    Generating resources for each step, so in the end you get a resource with a
    tree like this: `('this', 'is', 'an', 'api', 'resource')`

    Since at least two classes use this functionality, do not forget to
    override _new_element. This method specify what to build as a resource and
    how to build it.
    """
    def __init__(self, interface, node, tree):
        self.interface = interface
        if node:
            tree = tree + (node,)
        self.tree = tree

    def __eq__(self, other):
        return self.interface == other.interface and \
            self.tree == other.tree

    def __getattr__(self, attr):
        interface = self.interface
        if attr not in interface:
            interface[attr] = {}
        return self._new_element(interface[attr], attr, self.tree)

    def _new_element(self, interface, node, tree):
        """What to build as a resource in the next step (and how to do it)"""
        raise NotImplementedError('Implment in your subclass')


class Resource(ResourceElement):
    def __init__(self, request, interface, node, tree):
        super(Resource, self).__init__(interface, node, tree)
        self.request = request

    def _new_element(self, interface, node, tree):
        return Resource(self.request, interface, node, tree)

    def __eq__(self, other):
        return self.request == other.request and \
            super(Resource, self).__eq__(other)

    def __call__(self, **kwargs):
        return self._make_request(**kwargs)

    def _validate_arguments(self, kwargs):
        """Validate arguments taking care of queries in the names"""
        keys = set(key.split(':')[0] for key in kwargs.keys())
        for required in self.interface.get('required', []):
            if required not in keys:
                raise ValueError('Missing required argument: %s' % required)

    def _validate_method(self, kwargs):
        method = kwargs.pop('method', self.interface.get('method'))
        if not method:
            raise InterfaceNotDefined(
                'Interface is not defined, you must pass ``method``'
                ' (HTTP Method).')
        return method

    def _make_request(self, **kwargs):
        self._validate_arguments(kwargs)
        method = self._validate_method(kwargs)
        return self.request(method, '/'.join(self.tree), kwargs)


class DisqusRequest(object):
    headers = {'User-Agent': 'disqus-python/%s' % __version__}
    error_map = {
        13: RateLimitError,
        14: RateLimitError,
        18: InvalidAccessToken,
    }
    host = 'disqus.com'

    def __init__(self, default_params, version, conn=HTTPSConnection):
        self.__defaults = default_params
        self.__version = version
        self.__conn = conn

    def _update_params(self, kwargs):
        for name, value in self.__defaults.items():
            if value is None:
                continue
            if name not in kwargs:
                kwargs[name] = value

    def __call__(self, method, path, kwargs):
        self._update_params(kwargs)
        params = params_list(kwargs)
        # Adjust path
        path = '/api/%s/%s.json' % (self.__version, path)

        # Adjust data based on the method
        if method == 'GET':
            path = '%s?%s' % (path, urlencode(params))
            data = ''
        else:
            data = urlencode(params)

        conn = self.__conn(self.host)
        conn.request(method, path, data, self.headers)

        response = conn.getresponse()
        # Let's coerce it to Python
        data = simplejson.loads(response.read())

        if response.status != 200:
            exception_class = self.error_map.get(data['code'], APIError)
            raise exception_class(data['code'], data['response'])

        if isinstance(data['response'], list):
            return Result(data['response'], data.get('cursor'))
        return data['response']


def params_list(kwargs):
    params = []
    for key, value in kwargs.items():
        if isinstance(value, (list, tuple)):
            params.extend([(key, list_val) for list_val in value])
        else:
            params.append((key, value))
    return params


def load_interfaces():
    return simplejson.loads(open(os.path.join(
        os.path.dirname(__file__), 'interfaces.json'), 'r').read())


class DisqusAPI(ResourceElement):
    def __init__(self, secret_key=None, public_key=None, access_token=None,
                 version='3.0'):
        super(DisqusAPI, self).__init__(load_interfaces(), None, ())

        default_params = dict(
            api_secret=secret_key,
            api_key=public_key,
            access_token=access_token)
        self.make_request = DisqusRequest(default_params, version)

    def _new_element(self, interface, node, tree):
        return Resource(self.make_request, interface, node, tree)
