import sys

# pragma: no cover
PY3 = sys.version_info[0] == 3

# URL imports
if PY3:
    from urllib.parse import urlencode, urlparse
else:
    from urllib import urlencode
    import urlparse

# HTTPlib
if PY3:
    from http.client import HTTPSConnection
else:
    from httplib import HTTPSConnection
