byu-ws-python-sdk
=================

A Python SDK for authenticating to BYU REST web services.  To do this, the library provides methods to generate the
  required Authorization HTTP header for your REST web service calls.

The sdk now supports both Python 2.7 and Python 3.3.

Here is an ipython session showing the API.  I wrapped some of the output for readability.

    Pauls-MacBook-Pro:~ paul$ ipython
    Python 2.7.1 (r271:86832, Jun 16 2011, 16:59:05)
    Type "copyright", "credits" or "license" for more information.

    IPython 0.13.1 -- An enhanced Interactive Python.
    ?         -> Introduction and overview of IPython's features.
    %quickref -> Quick reference.
    help      -> Python's own help system.
    object?   -> Details about 'object', use 'object??' for extra details.

    In [1]: import byu_ws_sdk as sdk

    In [2]: url='https://ws.byu.edu/example/authentication/hmac/services/v1/exampleWS'

    In [3]: key = 'your-api-key'

    In [4]: shared_secret = 'your-shared-secret'

    In [5]: headerVal = sdk.get_http_authorization_header(key, shared_secret, sdk.KEY_TYPE_API, sdk.ENCODING_URL,
                            url=url, actor='pd123', httpMethod=sdk.HTTP_METHOD_GET, actorInHash=True)

    In [6]: import requests

    In [7]: res = requests.get(url, headers={'Authorization': headerVal})

    In [8]: res.status_code
    Out[8]: 200

    In [9]: res.content
    Out[9]: '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
            <message xmlns="http://ws.byu.edu/namespaces/authentication/example/v1">
            <greeting>Hello There Paul Eden</greeting></message>'

    In [10]: sdk.<tab>
    sdk.ENCODING_NONCE                 sdk.get_pretty_xml
    sdk.ENCODING_URL                   sdk.get_ws_session
    sdk.HTTP_METHOD_DELETE             sdk.hashlib
    sdk.HTTP_METHOD_GET                sdk.hmac
    sdk.HTTP_METHOD_POST               sdk.make_sha512_mac
    sdk.HTTP_METHOD_PUT                sdk.nonce_encode
    sdk.KEY_TYPE_API                   sdk.os
    sdk.KEY_TYPE_WSSESSION             sdk.requests
    sdk.VALID_ENCODING_TYPES           sdk.requests_config
    sdk.VALID_HTTP_METHODS             sdk.send_ws_request
    sdk.VALID_KEY_TYPES                sdk.simplejson
    sdk.base64                         sdk.time
    sdk.base64encode_string            sdk.url_encode
    sdk.core                           sdk.valid_encoding_types
    sdk.get_body_from_file             sdk.valid_http_method
    sdk.get_formatted_response         sdk.valid_key_type
    sdk.get_http_authorization_header  sdk.xml
    sdk.get_nonce

    In [10]: help(sdk.get_http_authorization_header)
    Help on function get_http_authorization_header in module byu_ws_sdk.core:

    get_http_authorization_header(apiKey, sharedSecret, keyType, encodingType, url='',
            requestBody=None, actor=None, contentType=None, httpMethod=None,
            demo=False, actorInHash=False)
        Encode the request to get the Authorization header value.

        An example return value type is (for wsSession keys (the ones that expire in less than a day))
        URL-Encoded-WsSession-Key Xh348rh4YbfYH9H9IMwv,2iJdLY/nY...MA...EM9V+/P229jBCcOUuw==,2011-08-19 09:02:30

    In [11]: help(sdk.get_ws_session)
    Help on function get_ws_session in module byu_ws_sdk.core:

    get_ws_session(casNetId, casPassword, timeout=1)
        get a wsSession keypair (apiKey/wsId and sharedSecret)

        timeout is the number of minutes before the wsSession key expires.
        valid values for timeout are 1 to 480 in minutes (480 minutes = 8 hours)

        return value example is
        {'personId': '123456789', 'apiKey': '5f_TzU3jdjX6s7DklHA8',
        'expireDate': '2011-07-07 19:12:43',
        'sharedSecret': 'gKLR8oDsNK4jyvKyWZtsFoiwuvLhwWpsBDTNJo_D'}

    In [12]: help(sdk.get_nonce)
    Help on function get_nonce in module byu_ws_sdk.core:

    get_nonce(apiKey, actor='')
        get a nonce key and value from the api-key

        Note, that the nonce returned here, at least currently, has a 5 minute hard-coded expiration.

        return value example is
        {'nonceKey': '57921',
         'nonceValue': 'G4qPJr5L3xI3KjXPw0g1mgWY8bzInQts7uctUfTAINm5ov3WCbXqRrTlFyECiiY/8rKGIqGUNDMxI9HlFvDEKg=='}


## BYU Models
This package also provides some models to represent people at BYU. The `Person` model can be instantiated manually and used manually. By taking advantage of the `PersonFactory`, you can get an instantiated `Person` model that has information already filled out populated from various BYU web services. For example:

    1 >>> from byu_ws_sdk.helpers import PersonFactory
    2 >>> pf = PersonFactory()  # assuming you have BYU_WS_KEY and BYU_WS_SECRET environment variables defined. Otherwise they should be passed in.
    3 >>> person = pf.get_person('jcougar2', ['full_name', 'byu_id', 'email'])
    4 >>> person.full_name
    4: u'Joseph Q. Cougar'

    5 >>> person.byu_id
    5: u'64-586-3824'

    6 >>> person.email
    6: u'joe@primo.exlibris.com'

    7 >>> person.net_id
    7: 'jcougar2'

    8 >>> pf.get_memberships(person, ['Employee', 'Student', 'test_gro_group'])
    8: <byu_ws_sdk.models.Person at 0x7f70aa778d90>

    9 >>> person.memberships
    9: {'Employee': False, 'Student': False, 'test_gro_group': True}

    10 >>> person.is_member('Employee')
    10: False

    11 >>> person.is_member('test_gro_group')
    11: True
