from urlparse import urlparse

from django.contrib.auth.models import User
from django.test import TestCase

from gonzo.utils import twitter

class TwitterTest(TestCase):
    def setUp(self):
        self.is_enabled = twitter.is_enabled()
        self.is_self_enabled = twitter.is_self_enabled()
        self.user = User.objects.create_user('testdude', '', 'testpassword')
        self.enabled_user = User.objects.create_user('enabled', '', 'enabled')
        profile = self.enabled_user.get_profile()
        profile.twitter_screen_name = 'enabled'
        profile.twitter_oauth_token = 'xxxxx'
        profile.twitter_oauth_secret = 'yyyyy'
        profile.save()

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

