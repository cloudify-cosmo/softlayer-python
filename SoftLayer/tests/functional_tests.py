"""
    SoftLayer.tests.functional_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
import os

import SoftLayer
from SoftLayer import testing
from SoftLayer import transports


def get_creds():
    for key in 'SL_USERNAME SL_API_KEY'.split():
        if key not in os.environ:
            raise testing.unittest.SkipTest(
                'SL_USERNAME and SL_API_KEY environmental variables not set')

    return {
        'endpoint': (os.environ.get('SL_API_ENDPOINT') or
                     SoftLayer.API_PUBLIC_ENDPOINT),
        'username': os.environ['SL_USERNAME'],
        'api_key': os.environ['SL_API_KEY']
    }


class UnauthedUser(testing.TestCase):
    def test_failed_auth(self):
        client = SoftLayer.Client(
            username='doesnotexist', api_key='issurelywrong', timeout=20)
        self.assertRaises(
            SoftLayer.SoftLayerAPIError,
            client['SoftLayer_User_Customer'].getPortalLoginToken)

    def test_no_hostname(self):
        try:
            request = transports.Request()
            request.endpoint = 'http://notvalidsoftlayer.com'
            request.service = 'SoftLayer_Account'
            request.method = 'getObject'
            request.id = 1234

            # This test will fail if 'notvalidsoftlayer.com' becomes a thing
            transport = transports.XmlRpcTransport()
            transport(request)
        except SoftLayer.SoftLayerAPIError as ex:
            self.assertIn('not known', str(ex))
            self.assertIn('not known', ex.faultString)
            self.assertEqual(ex.faultCode, 0)
        else:
            self.fail('No Exception Raised')


class AuthedUser(testing.TestCase):
    def test_service_does_not_exist(self):
        creds = get_creds()
        client = SoftLayer.Client(
            username=creds['username'],
            api_key=creds['api_key'],
            endpoint_url=creds['endpoint'],
            timeout=20)

        try:
            client["SoftLayer_DOESNOTEXIST"].getObject()
        except SoftLayer.SoftLayerAPIError as e:
            self.assertEqual(e.faultCode, '-32601')
            self.assertEqual(e.faultString, 'Service does not exist')
            self.assertEqual(e.reason, 'Service does not exist')
        else:
            self.fail('No Exception Raised')

    def test_get_users(self):
        creds = get_creds()
        client = SoftLayer.Client(
            username=creds['username'],
            api_key=creds['api_key'],
            endpoint_url=creds['endpoint'],
            timeout=20)

        found = False
        results = client["Account"].getUsers()
        for user in results:
            if user.get('username') == creds['username']:
                found = True
        self.assertTrue(found)

    def test_result_types(self):
        creds = get_creds()
        client = SoftLayer.Client(
            username=creds['username'],
            api_key=creds['api_key'],
            endpoint_url=creds['endpoint'],
            timeout=20)
        result = client['SoftLayer_User_Security_Question'].getAllObjects()
        self.assertIsInstance(result, list)
        self.assertIsInstance(result[0], dict)
        self.assertIsInstance(result[0]['viewable'], int)
        self.assertIsInstance(result[0]['question'], str)
        self.assertIsInstance(result[0]['id'], int)
        self.assertIsInstance(result[0]['displayOrder'], int)
