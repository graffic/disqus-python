from disqusapi.exceptions import APIError
from disqusapi.tests import unittest


class TestAPIError(unittest.TestCase):
    def test_init_code(self):
        self.assertEqual(12, APIError(12, None).code)

    def test_init_message(self):
        self.assertEqual('msg', APIError(12, 'msg').message)

    def test_repr(self):
        self.assertEqual(
            '<disqusapi.APIError 1: my message>',
            repr(APIError(1, 'my message')))
