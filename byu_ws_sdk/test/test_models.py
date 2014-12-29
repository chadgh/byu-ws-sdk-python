import unittest
from byu_ws_sdk.models import Person


class TestPersonModel(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_instantiate_person(self):
        net_id = 'test'
        actor = 'test2'
        p = Person(net_id)
        pb = Person(net_id, actor)

        self.assertEquals(p.net_id, net_id)
        self.assertEquals(p.actor, net_id)
        self.assertEquals(str(p), net_id)
        self.assertEquals(p._raw_service_responses, {})
        self.assertEquals(p.first_name, None)
        self.assertEquals(p.byu_id, None)
        self.assertEquals(pb.net_id, net_id)
        self.assertEquals(pb.actor, actor)
        self.assertEquals(str(pb), net_id)
        self.assertEquals(pb._raw_service_responses, {})
        self.assertEquals(pb.first_name, None)
        self.assertEquals(pb.byu_id, None)

    def test_membership_access_person(self):
        p = Person('test')
        p.add_membership('Employee')
        p.add_membership('Student', False)
        p.add_membership('Staff', True)
        p.add_membership('my_gro_group', is_member=True)

        self.assertEquals(p.is_member('Employee'), True)
        self.assertEquals(p.is_member('Student'), False)
        self.assertEquals(p.is_member('Staff'), True)
        self.assertEquals(p.is_member('my_gro_group'), True)
        self.assertEquals(p.is_member('something_not_there'), False)

    def test_raw_service_response_access_person(self):
        p = Person('test')
        sr = {'a': 'testing'}
        p.set_raw_service_response('personsummary', sr)

        self.assertEquals(p.get_raw_service_response('personsummary'), sr)
        self.assertRaises(ValueError, lambda: p.get_raw_service_response('a'))
