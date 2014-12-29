from __future__ import unicode_literals


# Helper functions
def __make_name(given_name, surname, position):
    if position == 'L':
        name = "{given_name} {surname}"
    else:
        name = "{surname} {given_name}"
    return name.format(given_name=given_name, surname=surname).strip()


def __get_surname_position(response, person):
    surname_position_func = SERVICE['attributes']['surname_position']
    return surname_position_func(response, person)


# Attribute parsing functions
def _name(response, person):
    surname_position = __get_surname_position(response, person)
    first_name = SERVICE['attributes']['first_name'](response, person)
    surname = SERVICE['attributes']['surname'](response, person)
    return __make_name(first_name, surname, surname_position)


def _full_name(response, person):
    surname_position = __get_surname_position(response, person)
    given_names = SERVICE['attributes']['given_names'](response, person)
    surname = SERVICE['attributes']['surname'](response, person)
    return __make_name(given_names, surname, surname_position)


# Service response parser and information
def parse_response(response, person, information):
    if response:
        attributes = SERVICE['attributes'].keys()
        for info in [i for i in information if i in attributes]:
            value = SERVICE['attributes'][info](response, person)
            setattr(person, info, value)
    return person


SERVICE = {
    'name': 'personnames',
    'url': 'https://ws.byu.edu/rest/v2.0/identity/person/PRO/personNames.cgi/{net_id}.json',  # noqa
    'root': 'PersonNamesService',
    'attributes': {
        'first_name': lambda res, p: res['preferred_name']['preferred_first_name'],  # noqa
        'full_name': _full_name,
        'given_names': lambda res, p: res['official_name']['rest_of_name'],
        'name': _name,
        'sort_name': lambda res, p: res['official_name']['sort_name'],
        'surname': lambda res, p: res['official_name']['surname'],
        'surname_position': lambda res, p: res['official_name']['surname_position'],  #noqa
    },
}
