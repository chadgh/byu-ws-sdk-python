from __future__ import unicode_literals


def parse_response(response, person, group):
    person.add_membership(group, response.get('isMember', False))
    return person


SERVICE = {
    'name': 'ismember',
    'url': 'https://ws.byu.edu/rest/v1/identity/person/isMember/{group_id}/{net_id}.json',  # noqa
    'root': 'isMember Service',
}
