disqus-python
~~~~~~~~~~~~~

Let's start with installing the API:

.. code:: console

    $ pip install disqus-python

Use the API by instantiating it, and then calling the method through dotted notation chaining:

.. code:: python

    from disqusapi import DisqusAPI
    disqus = DisqusAPI('MyApplicationSecretKey')
    for result in disqus.trends.listThreads():
        print(result)

The available `DisqusAPI` parameters are:

- `secret_key`: your applicaiton public key
- `public_key`: your application public key (You need one of these keys)
- `access_token`: authentication access_token 
- `version`: Endpoint version,. It defaults to '3.0'


Parameters (including the ability to override version, api_secret, and format) are passed as 
keyword arguments to the resource call:

.. code:: python

    disqus.posts.details(post=1, version='3.0')

Paginating through endpoints is easy as well:

.. code:: python

    from disqusapi import DisqusAPI, Paginator

    api = DisqusAPI('MyApplicationSecretKey')
    paginator = Paginator(api.trends.listThreads, forum='disqus')
    for result in paginator:
        print result

    # pull in a maximum of 500 results (this limit param differs from the endpoint's limit param)
    for result in paginator(limit=500):
        print result

Documentation on all methods, as well as general API usage can be found at http://disqus.com/api/
