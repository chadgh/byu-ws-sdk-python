from __future__ import unicode_literals

from datetime import datetime

SERVICE_DATE_FORMAT = '%Y-%m-%d'


# Helper functions
def __make_date(date_string):
    if date_string:
        try:
            return datetime.strptime(date_string, SERVICE_DATE_FORMAT).date()
        except ValueError:
            pass
    return None


# Attribute parsing functions
def _byu_id_number(response, person):
    byu_id = SERVICE['attributes']['byu_id'](response, person)
    issue_number_func = SERVICE['attributes']['byu_id_issue_number']
    issue_number = issue_number_func(response, person)
    return "{0} {1}".format(byu_id, issue_number)


def _employee_role_parts(response, person):
    roles = SERVICE['attributes']['employee_role'](response, person)
    return roles.split('/')


def _hired_date(response, person):
    date_string = (response['employee_information']
                   .get('date_hired', {})
                   .get('date', ''))
    return __make_date(date_string)


def _retirement_date(response, person):
    date_string = response['employee_information'].get('retirement_date', '')
    return __make_date(date_string)


def _email(response, person):
    unlisted = response['contact_information']['email_address_unlisted']
    email = response['contact_information']['email']
    if not unlisted or person.net_id == person.actor:
        return email
    return 'Unlisted'


# Service response parser and information
def parse_response(response, person, information):
    if response:
        attributes = SERVICE['attributes'].keys()
        for info in [i for i in information if i in attributes]:
            value = SERVICE['attributes'][info](response, person)
            setattr(person, info, value)
    return person


SERVICE = {
    'name': 'personsummary',
    'url': 'https://ws.byu.edu/rest/v2.0/identity/person/PRO/personSummary.cgi/{net_id}.json',  # noqa
    'root': 'PersonSummaryService',
    'remove': [
        'identifiers.ssn',
    ],
    'attributes': {
        'byu_id': lambda res, p: res['identifiers']['byu_id'],
        'byu_id_issue_number': lambda res, p: res['identifiers']['byu_id_issue_number'],  # noqa
        'byu_id_number': _byu_id_number,
        'department': lambda res, p: res['employee_information']['department'],
        'email': _email,
        'employee_role': lambda res, p: res['employee_information']['employee_role'],  #noqa
        'employee_role_parts': _employee_role_parts,
        'gender': lambda res, p: res['personal_information']['gender'],
        'hired_date': _hired_date,
        'job_title': lambda res, p: res['employee_information']['job_title'],
        'person_id': lambda res, p: res['identifiers']['person_id'],
        'retirement_date': _retirement_date,
        'student_role': lambda res, p: res['student_information']['student_role'],  # noqa
    },
}
