NEXT VERSION
============

2013/2014

- Python 3 support (3.3 tested in tox)
- Refactored and covered with tests.
- Removed dummy properties in DisqusAPI
- Improved README.rst

0.4.2
=====

2012-01-25

- Updated requirements in setup.py
- Fixed again behavioir on missing api_secret or api_public

0.4.1
=====

2011-11-09

- Fixed behavior when api_secret or api_public are not set.

0.4.0
=====

2011-11-09

* Removed signed requests (Disqus has deprecated them).
* Change all endpoints to use SSL.


0.3.4
=====

2011-11-08

- No changes, just a version bump

0.3.3
=====

2012-11-08

- Remove method argument from calls instead of just reading it.

0.3.2
=====


- Added support for undefined interfaces.
- Added support for mapping error codes to different exceptions.

0.3.1
=====

2011-11-02

- Fixed an issue with GET requests and the normalized request string.

0.3.0
=====

2011-11-01

- Added signed requests (you must pass public_key to DisqusAPI).
- Added support for OAuth (via access_token in signed requests).
- Moved Paginator into disqusapi.paginator
