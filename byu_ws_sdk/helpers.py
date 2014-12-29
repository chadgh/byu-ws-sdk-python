from __future__ import unicode_literals

from functools import partial
import os
import threading
try:
    from Queue import Queue
except ImportError:
    from queue import Queue
import time
import logging

from byu_ws_sdk.core import ENCODING_URL, HTTP_METHOD_GET, KEY_TYPE_API
from byu_ws_sdk.core import send_ws_request, get_http_authorization_header

from byu_ws_sdk import services
from byu_ws_sdk.services import ismember
from byu_ws_sdk.models import Person

log = logging.getLogger(__name__)

_get_header = partial(get_http_authorization_header,
                      keyType=KEY_TYPE_API,
                      encodingType=ENCODING_URL,
                      httpMethod=HTTP_METHOD_GET,
                      actorInHash=False,
                      )


def _threadable(func):
    def wrapped_func(q, *args, **kwargs):
        rtn = func(*args, **kwargs)
        q.put(rtn)

    def wrap(*args, **kwargs):
        q = Queue()
        t = threading.Thread(target=wrapped_func,
                             args=(q,) + args, kwargs=kwargs)
        t.daemon = False
        t.started = time.time()
        t.start()
        t.result = q
        return t

    return wrap


@_threadable
def _get_response(service, service_caller, information):
    response = {}
    if service['name'] == 'ismember':
        response = service_caller(service, group_id=information)
    else:
        log.debug('called service: {0}'.format(service['name']))
        if any([i in service['attributes'] for i in information]):
            response = service_caller(service)
    return response


def _remove_index(dictionary, index):
    depth = index.split('.')
    base = depth[-1]
    for attr in depth:
        if base in dictionary:
            del dictionary[base]
            break
        elif attr in dictionary:
            dictionary = dictionary[attr]


def _service_caller(service, net_id, actor, byu_key, byu_secret, **kwargs):
    if service['name'] == 'ismember':
        group_id = kwargs['group_id']
        del kwargs['group_id']
        url = service['url'].format(net_id=net_id, group_id=group_id)
    else:
        url = service['url'].format(net_id=net_id)
    auth_header = _get_header(byu_key,
                              byu_secret,
                              url=url,
                              actor=actor)
    headers = {'Authorization': auth_header}
    content, status_code, headers, response = send_ws_request(url,
                                                              HTTP_METHOD_GET,
                                                              headers=headers,
                                                              **kwargs)
    if status_code == 200:
        try:
            response = response.json()
            response = response[service['root']]['response']
            for to_remove in service.get('remove', []):
                _remove_index(response, to_remove)
            return response
        except:
            return BYUServiceError("Service invalid: {0}".format(url),
                                   'unknown')
    else:
        return BYUServiceError("Service failed: {0} ({1})".format(url,
                                                                  status_code),
                               content)


class PersonFactory(object):
    def __init__(self, actor=None, byu_key=None, byu_secret=None,
                 **extra_request_kwargs):
        self.byu_key = byu_key
        if byu_key is None:
            self.byu_key = os.environ.get('BYU_WS_KEY')

        self.byu_secret = byu_secret
        if byu_secret is None:
            self.byu_secret = os.environ.get('BYU_WS_SECRET')

        if self.byu_key is None or self.byu_secret is None:
            raise BYUServiceError(("Must provide a BYU web service key and "
                                   "shared secret."),
                                  BYUServiceError.INVALID_CREDENTIALS)

        if 'timeout' not in extra_request_kwargs:
            extra_request_kwargs['timeout'] = 3  # default timeout to 3 seconds

        self.extra_request_kwargs = extra_request_kwargs
        self.actor = actor

    def _get_service_caller(self, net_id, actor):
        """
        Returns a service_caller function.

        Arguments:
            net_id - netId of the person to get information about.
            actor - netId of the person requesting the information.
        """
        return partial(_service_caller,
                       net_id=net_id,
                       actor=actor,
                       byu_key=self.byu_key,
                       byu_secret=self.byu_secret,
                       **self.extra_request_kwargs)

    def get_person(self, net_id, information=None):
        information = information if information else []

        actor = self.actor if self.actor else net_id
        person = Person(net_id, actor)

        call_service = self._get_service_caller(person.net_id, person.actor)
        started = time.time()
        responses = self._request_information(call_service, information)
        exceptions = []
        for name, response in responses.items():
            value = response[1].result.get()
            done = time.time() - response[1].started
            log.debug("service done: {0} (took {1} sec)".format(name, done))
            if value == '':
                continue
            if isinstance(value, BYUServiceError):
                exceptions.append(value)
            else:
                func = response[0]
                person.set_raw_service_response(name, value)
                person = func(value, person, information)
        if exceptions:
            raise BYUServiceError("Exceptions on service calls", exceptions)
        done = time.time() - started
        log.debug("all services took {0} sec".format(done))
        return person

    def get_memberships(self, person, groups, actor=None):
        """
        Person instance populated with additional group membership information.

        Arguments:
            person - a object instance that has a add_membership method taking
                     the group_id and a boolean indicating membership.
            groups - a list of group_ids to check membership on.
            actor - the actor to use to check group memberships
                    (default person.actor)
        """
        actor = actor if actor else person.actor
        call_service = self._get_service_caller(person.net_id, actor)
        responses = self._request_memberships(call_service, groups)
        exceptions = []
        for group, thread in responses:
            value = thread.result.get()
            if value == '':
                continue
            if isinstance(value, BYUServiceError):
                exceptions.append(value)
            else:
                person = ismember.parse_response(value, person, group)
        if exceptions:
            raise BYUServiceError("Exceptions on service calls", exceptions)

        return person

    def _request_information(self, caller, information):
        rtn_services = {}
        for service in services.ALL_PERSON_SERVICES:
            module_name = '.'.join(['byu_ws_sdk.services', service])
            service_module = __import__(module_name,
                                        fromlist=['SERVICE', 'parse_response'])
            parser = service_module.parse_response
            service = service_module.SERVICE
            log.debug("calling service: {0}".format(service['name']))
            rtn_services[service['name']] = (parser,
                                             _get_response(service,
                                                           caller,
                                                           information))
        return rtn_services

    def _request_memberships(self, caller, groups):
        rtn_groups = []
        for group in groups:
            rtn_groups.append((group, _get_response(ismember.SERVICE,
                                                    caller,
                                                    group)))
        return rtn_groups


class BYUServiceError(Exception):
    INVALID_CREDENTIALS = 'Invalid credentials provided.'

    def __init__(self, message, error):
        super(BYUServiceError, self).__init__(message)
        self.error = error

    def __str__(self):
        return "{0.message}: \n\n{0.error}".format(self)
