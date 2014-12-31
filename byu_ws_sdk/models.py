from __future__ import unicode_literals


class Person(object):

    """A person at BYU."""

    def __init__(self, net_id, actor=None):
        """
        Represents a person (students/faculty/staff) at BYU.

        Arguments:
            net_id - the NetId of the person.
            actor - the NetId of the person wanting the information,
                    (default: net_id)
        """
        self.net_id = net_id
        self.actor = actor if actor else net_id
        self._raw_service_responses = {}
        # personnames service attributes
        self.first_name = None
        self.full_name = None
        self.given_names = None
        self.name = None
        self.sort_name = None
        self.surname = None
        self.surname_position = None
        # personsummary service attributes
        self.byu_id = None
        self.byu_id_issue_number = None
        self.byu_id_number = None
        self.courses = None
        self.department = None
        self.email = None
        self.employee_role = None
        self.employee_role_parts = None
        self.gender = None
        self.hired_date = None
        self.job_title = None
        self.person_id = None
        self.retirement_date = None
        self.student_role = None
        self.memberships = {}

    def get_raw_service_response(self, service_name):
        rtn = self._raw_service_responses.get(service_name, None)
        if rtn is None:
            raise ValueError('No raw service response for {}'.format(
                service_name))
        return rtn

    def set_raw_service_response(self, service_name, response):
        self._raw_service_responses[service_name] = response

    def is_member(self, group_id):
        return self.memberships.get(group_id, False)

    def add_membership(self, group_id, is_member=True):
        self.memberships[group_id] = is_member

    def __str__(self):
        return str(self.__unicode__())

    def __unicode__(self):
        return self.net_id


class Course(object):

    """
    A course at BYU.

    The resulting instantiated instance will have the following attributes.

    catalog_entry - the catalog_entry value passed in on instantiation
    teaching_area - the teaching_area value passed in on instantiation
    instructor - the instructor value passed in on instantiation
    course_number - the first portion of the catalog_entry value, before the -
    section_number - the second portion of the catalog_entry value, after -
    normalized_teaching_area - lowercased and space replaced teaching_area
    """

    def __init__(self, catalog_entry, teaching_area, instructor):
        """
        A BYU course is instantiated with the following required arguments.

        Arguments:
            catalog_entry - catalog course number of the format,
                            [course number]-[section number]
            teaching_area - the teaching area of the course
            instructor - instructors name
        """
        self.catalog_entry = catalog_entry.strip()
        self.teaching_area = teaching_area.strip()
        self.instructor = instructor.strip()
        self.course_number = self.catalog_entry.split('-')[0]
        self.section_number = self.catalog_entry.split('-')[1]
        self.normalized_teaching_area = (self
                                         .teaching_area
                                         .lower()
                                         .replace(' ', ''))

    def __str__(self):
        return str(self.__unicode__())

    def __unicode__(self):
        return ("{0.teaching_area} {0.catalog_entry} by {0.instructor}"
                .format(self))

    def __repr__(self):
        return ("Course('{0.catalog_entry}', '{0.teaching_area}', "
                "'{0.instructor}')".format(self))
