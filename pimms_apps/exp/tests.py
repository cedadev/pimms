from django.test import TestCase

class ViewsTestCase(TestCase):
    def test_index(self):
        resp = self.client.get('/cimexpgen/')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('message' in resp)