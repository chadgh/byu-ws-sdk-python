"""
The code that generates the Authorization HTTP header.
"""
__author__ = 'paul_eden@byu.edu'
import os
import xml.dom.minidom

try:
    import simplejson as json
except ImportError:
    import json

import hashlib
import hmac
import base64
import sys
import time
import requests

# Singletons for use in validation and conformity of arguments
ENCODING_NONCE = "Nonce"
ENCODING_URL = "URL"
KEY_TYPE_API = "API"
KEY_TYPE_WSSESSION = "WsSession"
HTTP_METHOD_GET = "GET"
HTTP_METHOD_PUT = "PUT"
HTTP_METHOD_POST = "POST"
HTTP_METHOD_DELETE = "DELETE"
VALID_HTTP_METHODS = [HTTP_METHOD_GET, HTTP_METHOD_PUT, HTTP_METHOD_POST, HTTP_METHOD_DELETE]
VALID_KEY_TYPES = [KEY_TYPE_API, KEY_TYPE_WSSESSION]
VALID_ENCODING_TYPES = [ENCODING_NONCE, ENCODING_URL]


def valid_http_method(method):
    return method.upper() in VALID_HTTP_METHODS


def valid_key_type(key_type):
    return key_type in VALID_KEY_TYPES


def valid_encoding_types(encoding_type):
    return encoding_type in VALID_ENCODING_TYPES


def get_body_from_file(file_name):
    if file_name and os.path.exists(file_name):
        return file(file_name, "rb").read().rstrip("\n")
    else:
        return ""


def get_pretty_xml(xml_str):
    return xml.dom.minidom.parseString(xml_str).toprettyxml()


def get_formatted_response(headers, response_str):
    if headers["Content-Type"] in "text/xml application/xml".split(' '):
        try:
            return get_pretty_xml(response_str)
        finally:
            return response_str
    return response_str

#### Key Retrieval Functions ####


def get_ws_session(casNetId, casPassword, casTimeout=1, **kwargs):
    """
    get a wsSession key pair (apiKey/wsId and sharedSecret)

    casTimeout is the number of minutes before the wsSession key expires.
    valid values for casTimeout are 1 to 480 in minutes (480 minutes = 8 hours)

    return value example is
    {'personId': '524246202', 'apiKey': '5f_TzU3jdjX6s7DklHA8',
    'expireDate': '2011-07-07 19:12:43',
    'sharedSecret': 'gKLR8oDsNK4jyvKyWZtsFoiwuvLhwWpsBDTNJo_D'}
    """
    cas_user_dict = {"timeout": casTimeout, "username": casNetId, "password": casPassword}
    data = "timeout=%(timeout)s&password=%(password)s&netId=%(username)s" % cas_user_dict
    content_type = "application/x-www-form-urlencoded; charset=UTF-8"
    if kwargs.get('headers'):
        kwargs['headers']['Content-Type'] = content_type
    else:
        kwargs['headers'] = {'Content-Type': content_type}
    response = requests.post("https://ws.byu.edu/authentication/services/rest/v1/ws/session", data=data, **kwargs)
    response.raise_for_status()
    body = response.content
    if not body:
        raise Exception("The WsSession-granting web service did not provide a WsSession."
                        "  Perhaps the username and password supplied are not valid?")
    return json.loads(body)


def get_nonce(apiKey, actor="", **kwargs):
    """
    get a nonce key and value from the api-key

    Note, that the nonce returned here, at least currently, has a 5 minute hard-coded expiration.

    return value example is
    {'nonceKey': '57921',
     'nonceValue': 'G4qPJr5L3xI3KjXPw0g1mgWY8bzInQts7uctUfTAINm5ov3WCbXqRrTlFyECiiY/8rKGIqGUNDMxI9HlFvDEKg=='}
    """
    nonce_url = "https://ws.byu.edu/authentication/services/rest/v1/hmac/nonce/{0}{1}"
    if actor:
        actor = "/" + actor
    else:
        actor = ""  # in cases when actor == None or 'None' will be added to the URL
    response = requests.post(nonce_url.format(apiKey, actor), **kwargs)
    body = response.content
    try:
        rvalue = json.loads(body)
    except:
        print(body)
        raise
    return rvalue

# no need for a get_api_key method because that is not an automated process
# and is done once and the apiKey is long lived.

#### Encoding Functions ####


def _split_url(url):
    """
    Taking a url of the form:
    http://www.byu.edu/testing/123?p=1&q=true
    This function returns:
    www.byu.edu, /testing/123
    """
    tokens = url.split("://", 1)
    if len(tokens) > 1:
        url = tokens[1]
        # now url is www.byu.edu/testing/123?p=1&q=true
    tokens = url.split("?", 1)
    if len(tokens) > 1:
        url = tokens[0]
        # now url is www.byu.edu/testing/123
    tokens = url.split("/", 1)
    if len(tokens) > 1:
        host = tokens[0]
        request_uri = "/" + tokens[1]
    else:
        host = tokens[0]
        request_uri = "/"
    if ":" in host:
        # remove the :PORT if there
        host = host.split(":")[0]
    return host, request_uri


def _sort_params(params_str):
    """
    Taking params of the form:
    p=1&a=9&a=0
    This function returns:
    a=9,0&p=1
    As required by the security code
    """
    params = {}
    # params_str is now p=1&a=9&a=0
    tokens = params_str.split("&")
    # tokens is now ["p=1", "a=9", "a=0"]
    if len(tokens) == 1:
        return params_str  # no '&' as in "a=1" or "" as the whole params
    else:
        # now sort and join
        for token in tokens:
            key, value = token.split("=", 1)
            if not key in params.keys():
                params[key] = value
            else:
                params[key] = params[key] + "," + value
    return_value = "&".join(["%s=%s" % (key, params[key]) for key in sorted(params.keys())])
    return return_value


def base64encode_string(string, demo=False):
    if sys.version_info < (3,):
        rvalue = base64.encodestring(string).strip().replace(" ", "").replace("\n", "").replace("\r", "")
    else:
        rvalue1 = base64.encodebytes(string)
        rvalue = rvalue1.strip().decode('utf-8').replace('\n', '').replace('\r', '').encode('utf-8')
    if demo:
        print("// base64 encoding the hash to create (%s)" % rvalue)
    return rvalue


def make_sha512_mac(sharedSecret, string, demo=False):
    if demo:
        print("// Making a sha512 hash of (%s) with my private key" % string)
    if sys.version_info > (3,):  # if python 3 convert to binary bytes
        sharedSecret = sharedSecret.encode("utf-8")
        if not isinstance(string, bytes):
            string = string.encode("utf-8")
    return hmac.new(key=sharedSecret,
                    msg=string,
                    digestmod=hashlib.sha512).digest()


def url_encode(sharedSecret, current_timestamp, url, requestBody="", contentType=None, http_method=None, actor=None,
               demo=False, actorInHash=False):
    """
    URL encode the request

    Returns hmac
    """
    end_str = current_timestamp
    if actorInHash:
        if actor:
            end_str += actor
    item_to_encode = url + end_str
    exception_ct = "application/x-www-form-urlencoded"
    if requestBody:
        if contentType == exception_ct:
            host, request_uri = _split_url(url)
            item_to_encode = "%s\n%s\n%s\n%s" % (http_method.upper(),
                                                 host, request_uri, _sort_params(requestBody)) + end_str
            if demo:
                print("// There is something in the request "
                      "body and the content-type of the request is %s" % exception_ct)
        else:
            item_to_encode = requestBody + end_str
            if demo:
                print("// There is something in the request body")
    if demo:
        print("// We are URL Encoding the following (%s)" % item_to_encode)
    mac = make_sha512_mac(sharedSecret,
                          str(item_to_encode).encode("ascii"), demo)
    return base64encode_string(mac, demo)


def nonce_encode(sharedSecret, nonceValue, demo=False):
    """
    Nonce encode the request

    Returns hmac
    """
    if demo:
        print("// Nonce encoding (%s) with our private key" % nonceValue)
    mac = make_sha512_mac(sharedSecret, nonceValue)
    return base64encode_string(mac)

#### Functions to make the HTTP request to a secured web service ####


def get_http_authorization_header(apiKey, sharedSecret, keyType, encodingType, url="", requestBody=None, actor="",
                                  contentType=None, httpMethod=None, demo=False, actorInHash=False):
    """
    Encode the request to get the Authorization header value.

    An example return value type is (for wsSession keys (the ones that expire in less than a day))
    URL-Encoded-WsSession-Key Xh348rh4YbfYH9H9IMwv,2iJdLY/nY...MA...EM9V+/P229jBCcOUuw==,2011-08-19 09:02:30
    """
    current_timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    nonceKey = ""
    if not valid_key_type(keyType):
        raise Exception("keyType must be one of %s" % " or ".join(VALID_KEY_TYPES))

    if encodingType == ENCODING_URL:
        base64encoded_hmac = url_encode(sharedSecret, current_timestamp, url, requestBody, contentType, httpMethod,
                                        actor, demo, actorInHash)
    elif encodingType == ENCODING_NONCE:
        nonceDict = get_nonce(apiKey, actor)
        base64encoded_hmac = nonce_encode(sharedSecret, nonceDict["nonceValue"])
        nonceKey = nonceDict["nonceKey"]
    else:
        raise Exception("encodingType must be one of '%s'" % "' or '".join(VALID_ENCODING_TYPES))

    if sys.version_info > (3,):  # if python 3 convert from bytes to string
        base64encoded_hmac = base64encoded_hmac.decode("utf-8")

    assert len(base64encoded_hmac) == 88
    if encodingType == ENCODING_NONCE:
        return "Nonce-Encoded-%s-Key %s,%s,%s" % (keyType, apiKey, nonceKey, base64encoded_hmac)
    else:
        if actor:
            actor_value = "," + actor
        else:
            actor_value = ""
        return "%s-Encoded-%s-Key %s,%s,%s%s" % (
            encodingType, keyType, apiKey, base64encoded_hmac, current_timestamp, actor_value)


def send_ws_request(url, httpMethod, requestBody=None, **kwargs):
    """
    A simple example of how to call the web service once the
    the authorization_header_value is available.
    """
    if not valid_http_method(httpMethod):
        raise Exception(
            "The httpMethod passed in (%s) is not one of '%s'" % (httpMethod, "','".join(VALID_HTTP_METHODS)))
    response = getattr(requests, httpMethod.lower())(url, data=requestBody, **kwargs)
    return response.content, response.status_code, response.headers, response


def authorize_request(requestedUrl, authHeader, apiKey, sharedSecret,
                      actor='', **kwargs):
    """
    Returns the personId of a valid BYU authenticated request or None.

    None is returned if the request isn't valid for any reason.
    Arguments:
        requestedUrl  -- url requested using the authHeader given.
        authHeader    -- value of the Authorization header sent with the request.
        apiKey        -- your api key
        sharedSecret  -- your shared secret

    Keyword arguments:
        actor         -- the actor making this authorization request (default '')

    Also accepts any number of other keyword arguments that are passed directly
    to the calls to get_nonce and request.post
    """
    authUrl = ('https://ws.byu.edu/authentication/services/rest/'
               'v1/provider/URL-Encoded-API-Key/validate')

    if authHeader:
        wsId, messageDigest, timestamp = authHeader.split(',')
        wsId = wsId.split(' ')[1]
        nonce = get_nonce(apiKey, actor, **kwargs)
        data = {
            'wsId': wsId,
            'messageDigest': messageDigest,
            'timestamp': timestamp,
            'message': requestedUrl,
        }

        nonceDigest = nonce_encode(sharedSecret, nonce['nonceValue'])

        if sys.version_info > (3,):  # if python 3 convert from bytes to string
            nonceDigest = nonceDigest.decode("utf-8")

        auth = 'Nonce-Encoded-API-Key {0},{1},{2}'.format(apiKey,
                                                          nonce['nonceKey'],
                                                          nonceDigest)
        if kwargs.get('headers'):
            kwargs['headers']['Authorization'] = auth
        else:
            kwargs['headers'] = {'Authorization': auth}
        response = requests.post(authUrl,
                                 data=data,
                                 **kwargs)
        if response.status_code == 200:
            return response.json()['personId']

    return None
