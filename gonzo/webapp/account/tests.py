from django.test import TestCase
from django.test.client import Client

class TwitterAuthTest(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_1_new_user(self):
        c = Client()
        response = c.get("/account/twitter/login/")
        self.assertEquals(response.status_code, 302)
