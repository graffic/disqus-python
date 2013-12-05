from mock import Mock

from disqusapi import (
    Result,
    ResourceElement,
    Resource,
    DisqusRequest,
    params_list,
    DisqusAPI,
    load_interfaces)
from disqusapi.exceptions import (
    InterfaceNotDefined,
    APIError,
    InvalidAccessToken,
    RateLimitError)
from disqusapi.tests import unittest


class TestResult(unittest.TestCase):
    def test_init_response(self):
        self.assertEqual('hey', Result('hey').response)

    def test_init_cursor_given(self):
        self.assertEqual('cursor', Result('hey', cursor='cursor').cursor)

    def test_init_cursor_none(self):
        self.assertEqual({}, Result('hey').cursor)

    def test_repr(self):
        self.assertEqual('<Result: 1234>', repr(Result(1234)))

    def test_iter(self):
        self.assertEqual([0, 1], list(Result(range(2))))

    def test_len(self):
        self.assertEqual(6, len(Result('banana')))

    def test_slice(self):
        """Slice works without the deprecated getslice"""
        self.assertEqual([1, 3], Result(list(range(15)))[1:5:2])

    def test_getitem(self):
        self.assertEqual(1, Result([0, 1, 2])[1])

    def test_contains(self):
        self.assertTrue('a' in Result('banana'))


class MyResourceElement(ResourceElement):
    def _new_element(self, interface, attr, tree):
        return MyResourceElement(interface, attr, tree)


class TestResourceElement(unittest.TestCase):
    def test_init_interface(self):
        self.assertEqual(
            'interfaces',
            MyResourceElement('interfaces', None, ()).interface)

    def test_init_tree(self):
        self.assertEqual((), MyResourceElement(1, None, ()).tree)

    def test_init_node_changes_tree(self):
        self.assertEqual(
            (1, 2),
            MyResourceElement('iface', 2, (1,)).tree)

    def test_eq(self):
        one = MyResourceElement('iface', 2, (1,))
        two = MyResourceElement('iface', 2, (1,))
        self.assertEqual(one, two)

    def test_not_eq_iface(self):
        one = MyResourceElement('iface', node=2, tree=(1,))
        two = MyResourceElement('', node=2, tree=(1,))
        self.assertNotEqual(one, two)

    def test_getattr(self):
        interface = {'apple': {'orange': {'wine': 'good'}}}
        sut = MyResourceElement(interface, None, ()).apple.orange.wine
        expected = MyResourceElement('good', 'wine', ('apple', 'orange'))
        self.assertEqual(expected, sut)

    def test_getattr_undefined_interface(self):
        sut = MyResourceElement({}, 2, ()).supercalifragilisticexpialidocious
        self.assertEqual({}, sut.interface)

    def test_new_element(self):
        with self.assertRaises(NotImplementedError):
            ResourceElement({}, None, ()).test


class TestResource(unittest.TestCase):
    def test_init_request(self):
        self.assertEqual('req', Resource('req', {}, None, ()).request)

    def test_resource_element_api(self):
        sut = Resource('req', {}, None, ())
        self.assertEqual('req', sut.hey.request)

    def test_invalid_argument(self):
        with self.assertRaises(ValueError):
            Resource('req', {'required': ['test']}, None, ())()

    def test_invalid_method(self):
        with self.assertRaises(InterfaceNotDefined):
            Resource('req', {}, None, ())()

    def test_request(self):
        request = Mock()
        Resource(request, {'method': 'POST'}, 'b', ('a',))(a=1)
        request.assert_called_with('POST', 'a/b', {'a': 1})


class TestDisqusRequest(unittest.TestCase):
    def setUp(self):
        self.conn = Mock()
        self.request = self.conn.return_value.request
        response = self.conn.return_value.getresponse.return_value
        response.status = 200
        response.read.return_value = '{"response": 1}'
        self.response = response
        self.sut = DisqusRequest('secret', '3.0', self.conn)

    def set_error_code(self, code):
        self.response.status = 500
        self.response.read.return_value = (
            '{"response": [1, 2], "code": %d}' % code)

    def test_update_keys_secret(self):
        kwargs = {}
        self.sut('POST', 'a/b', kwargs)
        self.assertEqual('secret', kwargs['api_secret'])

    def test_connection(self):
        self.sut('POST', 'a/b', {})
        self.conn.assert_called_with(self.sut.host)

    def test_request_call(self):
        self.sut('POST', 'a/b', {})
        self.request.assert_called_with(
            'POST', '/api/3.0/a/b.json', 'api_secret=secret', self.sut.headers)

    def test_request_get(self):
        self.sut('GET', 'a/b', {})
        self.request.assert_called_with(
            'GET', '/api/3.0/a/b.json?api_secret=secret', '', self.sut.headers)

    def test_response(self):
        self.assertEqual(1, self.sut('POST', 'a/b', {}))

    def test_response_list(self):
        self.response.read.return_value = '{"response": [1, 2], "cursor": 3}'
        res = self.sut('POST', 'a/b', {})
        self.assertEqual(Result([1, 2], 3), res)

    def test_error(self):
        self.set_error_code(1)
        with self.assertRaises(APIError):
            self.sut('POST', 'a/b', {})

    def test_error_13(self):
        self.set_error_code(13)
        with self.assertRaises(RateLimitError):
            self.sut('POST', 'a/b', {})

    def test_error_14(self):
        self.set_error_code(14)
        with self.assertRaises(RateLimitError):
            self.sut('POST', 'a/b', {})

    def test_error_18(self):
        self.set_error_code(18)
        with self.assertRaises(InvalidAccessToken):
            self.sut('POST', 'a/b', {})


class TestParamsList(unittest.TestCase):
    def test_simple(self):
        self.assertEqual([('a', 1)], params_list({'a': 1}))

    def test_list(self):
        self.assertEqual([('a', 1), ('a', 2)], params_list({'a': [1, 2]}))

    def test_tuple(self):
        self.assertEqual([('a', 1), ('a', 2)], params_list({'a': (1, 2)}))


class TestDisqusAPI(unittest.TestCase):
    def test_init_interface(self):
        self.assertEqual(load_interfaces(), DisqusAPI('secret').interface)

    def test_init_tree(self):
        self.assertEqual((), DisqusAPI('secret').tree)

    def test_resource_element(self):
        sut = DisqusAPI('secret')
        self.assertEqual(
            Resource(sut.make_request, {}, 'hey', ()),
            sut.hey)
