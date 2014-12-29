import unittest
import byu_ws_sdk as oit
import getpass
import os


def get_input(prompt):
    try:
        _input = raw_input
    except NameError:
        _input = input
    return _input(prompt)


class TestOITWebServicesLibraryInput(unittest.TestCase):

    def test_ws_session(self):
        net_id = get_input("NetId: ")
        password = getpass.getpass()
        res = oit.get_ws_session(net_id, password, verify=False)
        self.assertTrue('personId' in res)

    def test_authorize_request(self):
        apiKey = os.getenv('BYU_API_KEY')
        sharedSecret = os.getenv('BYU_API_SECRET')
        if not apiKey:
            apiKey = get_input("API Key: ")
        if not sharedSecret:
            sharedSecret = getpass.getpass("Shared secret: ")
        headerValue = oit.get_http_authorization_header(apiKey,
                                                        sharedSecret,
                                                        oit.KEY_TYPE_API,
                                                        oit.ENCODING_URL,
                                                        "http://www.byu.edu/",
                                                        "")
        res = oit.authorize_request('http://www.byu.edu/', headerValue, apiKey,
                                    sharedSecret, verify=False)
        self.assertTrue(res is not None)


if __name__ == "__main__":
    unittest.main()
