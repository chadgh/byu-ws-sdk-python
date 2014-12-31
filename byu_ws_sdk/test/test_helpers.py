import unittest
from byu_ws_sdk.helpers import PersonFactory
import os


class TestPersonFactory(unittest.TestCase):
    def setUp(self):
        key = os.getenv('BYU_API_KEY')
        secret = os.getenv('BYU_API_SECRET')
        cert = os.getenv('BYU_API_CERT', False)
        self.pf = PersonFactory(
            byu_key=key,
            byu_secret=secret,
            verify=cert,
        )
        self.p = self.pf.get_person('jcougar2',
                                    ['first_name', 'full_name', 'byu_id'])

    def tearDown(self):
        pass

    def test_get_person(self):
        self.assertEquals(self.p.first_name, 'Joe')
        self.assertEquals(self.p.surname, None)
        self.assertEquals(self.p.full_name, 'Joseph Q. Cougar')
        self.assertEquals(self.p.byu_id, '64-586-3824')

    def test_get_memberships(self):
        person = self.pf.get_memberships(self.p, ['Employee', 'Student'])
        person = self.pf.get_memberships(self.p, ['test_gro_group'], 'jcougar2')
        self.assertEquals(person.is_member('Employee'), False)
        self.assertEquals(person.is_member('Student'), False)
        self.assertEquals(person.is_member('test_gro_group'), True)
