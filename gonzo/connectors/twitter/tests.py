from urlparse import urlparse

from django.contrib.auth.models import User
from django.test import TestCase

from gonzo.connectors import twitter

class TwitterTest(TestCase):
    def setUp(self):
        self.is_enabled = twitter.is_enabled()
        self.is_self_enabled = twitter.is_self_enabled()
        self.user = User.objects.create_user('testdude', '', 'testpassword')
        self.enabled_user = User.objects.create_user('enabled', '', 'enabled')

    def test_0_auth(self):
        try:
            self.assert_(twitter.get_auth())
            self.assertRaises(twitter.UserNotAuthorized,
                              lambda: twitter.get_auth_for_user(self.user))
            self.assert_(twitter.get_auth_for_user(self.enabled_user))
        except twitter.NotEnabled:
            self.assert_(not self.is_enabled)

    def test_1_self(self):
        try:
            self.assert_(twitter.get_auth_for_self())
            self.assert_(twitter.get_api_for_self())
        except twitter.SelfNotEnabled:
            self.assert_(not self.is_self_enabled)

    def test_3_get_auth_url(self):
        try:
            auth = twitter.get_auth()
            urlstr = auth.get_authorization_url()
            # Ensure it's "api.twitter.com" and that it's secured
            url = urlparse(urlstr)
            self.assertEquals(url.scheme, "https")
            self.assertEquals(url.hostname, "api.twitter.com")
        except twitter.NotEnabled:
            assert(not self.is_enabled)

    def test_4_api(self):
        try:
            self.assert_(twitter.get_api())
            self.assertRaises(twitter.UserNotAuthorized,
                              lambda: twitter.get_api_for_user(self.user))
            self.assert_(twitter.get_api_for_user(self.enabled_user))
        except twitter.NotEnabled:
            self.assert_(not self.is_enabled)


    def test_5_fill_profile(self):
        # It's easiest to test with a public profile.
        auth = twitter.get_auth_for_self()
        user = self.enabled_user
        profile = twitter.fill_profile(user, auth=auth)
        self.assert_(profile)
        self.assertEquals(profile.user_location, "Seattle, WA")
        self.assertEquals(user.first_name, "One Hour Photo")
        self.assertEquals(user.last_name, "Hunt!")
        self.assert_(profile.photo)
        self.assert_(profile.photo.url)
        self.assert_(profile.photo_width > 0)
        self.assert_(profile.photo_height > 0)

