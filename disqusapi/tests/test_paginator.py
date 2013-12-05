from disqusapi.tests import unittest
from disqusapi import Result
from disqusapi.exceptions import RateLimitError
from disqusapi.paginator import (
    ignore_limit,
    use_cursor,
    limit_amount,
    Paginator)


class TestIgnoreLimit(unittest.TestCase):
    def test_ok(self):
        def endpoint():
            return 1
        self.assertEqual(1, ignore_limit(endpoint)())

    def test_rate_limit(self):
        def endpoint():
            raise RateLimitError(14, 'error')
        self.assertEqual(Result([]), ignore_limit(endpoint)())

    def test_other_error(self):
        def endpoint():
            raise ValueError('error')
        with self.assertRaises(ValueError):
            ignore_limit(endpoint)()


class TestUseCursor(unittest.TestCase):
    def test_no_pages(self):
        def endpoint():
            return Result([1, 2])
        self.assertEqual([1, 2], list(use_cursor(endpoint)()))

    def test_one_page(self):
        def endpoint(cursor=None):
            if cursor is None:
                return Result([1, 2], cursor=dict(more=True, id=3))
            else:
                return Result([cursor])
        self.assertEqual([1, 2, 3], list(use_cursor(endpoint)()))


class TestLimitAmount(unittest.TestCase):
    def test_limited(self):
        def endpoint():
            return range(100)
        self.assertEqual(
            list(range(10)),
            list(limit_amount(endpoint, 10)()))

    def test_limit_too_big(self):
        def endpoint():
            return range(2)

        self.assertEqual([0, 1], list(limit_amount(endpoint, 10)()))


class TestPaginator(unittest.TestCase):
    def test_simple(self):
        def endpoint():
            return Result([1, 2])
        self.assertEqual([1, 2], list(Paginator(endpoint)))

    def test_limit(self):
        def endpoint():
            return Result([1, 2, 3, 4])
        self.assertEqual([1, 2], list(Paginator(endpoint)(limit=2)))

    def test_silence_limit(self):
        def endpoint(cursor=None):
            if cursor is not None:
                raise RateLimitError(14, 'error')
            else:
                return Result([1, 2], dict(more=True, id=3))
        self.assertEqual([1, 2], list(Paginator(endpoint)(silence_limit=True)))
