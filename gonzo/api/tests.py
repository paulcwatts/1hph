"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""
import json, time, pytz
import StringIO
from datetime import datetime, timedelta

from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User

from gonzo.hunt import models
from gonzo.hunt.tests import make_hunt
from gonzo.hunt import testfiles
from gonzo.account.models import Profile

class StringFile(StringIO.StringIO):
    def __init__(self,name,buffer):
        self.name = name
        #super(StringFile,self).__init__(buffer)
        StringIO.StringIO.__init__(self,buffer)

class HuntAPITest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('testdude','test@test.com','password')
        self.user.save()
        self.hunt = make_hunt(self.user,
                             'first test hunt',
                             'firsttest',
                             datetime.utcnow(),
                             vote_delta=timedelta(hours=1))

    def tearDown(self):
        self.hunt.delete()
        self.user.delete()

    def test_API(self):
        c = Client()
        response = c.get('/api/hunt/')
        self.failUnlessEqual(response.status_code,200)
        #self.failUnlessEqual(response['Content-Type'],'application/json')
        obj = json.loads(response.content)
        self.assert_(obj['hunts'])
        hunts = obj['hunts']
        self.assertEquals(len(hunts),1)
        # Follow the URLs and see what we get
        hunt = hunts[0]
        response = c.get(hunt['url'])
        self.failUnlessEqual(response.status_code,200)
        response = c.get(hunt['api_url'])
        self.failUnlessEqual(response.status_code,200)

        submit_url = hunt['submissions']
        ballot_url = hunt['ballot']
        hunt_comments_url = hunt['comments']

        # Ensure that the ballot url returns an error
        response = c.get(ballot_url)
        self.failUnlessEqual(response.status_code,400)

        response = c.get(submit_url)
        self.failUnlessEqual(response.status_code,200)
        #self.failUnlessEqual(response['Content-Type'],'application/json')
        # No submissions yet
        obj = json.loads(response.content)
        self.assertEquals(obj['submissions'],[])

        from StringIO import StringIO
        # TODO: Test submssion -- authenticated and anonymous
        # photo, latitude, longitude, source_via
        # First test an invalid file
        response = c.post(submit_url, { 'photo':
                                      StringFile("testfile.txt","This is an invalid photo"),
                                      'source_via': 'unit test' })
        self.failUnlessEqual(response.status_code, 400)
        f = testfiles.open_file('test1.jpg')
        response = c.post(submit_url, { 'photo': f, 'via': 'unit test' })
        self.failUnlessEqual(response.status_code, 201)
        #self.failUnlessEqual(response['Content-Type'],'application/json')
        photo1Url = response['Content-Location']

         # Ensure that the ballot url returns an error
        response = c.get(ballot_url)
        self.failUnlessEqual(response.status_code,400)

        # Now log in and submit a photo
        c.login(username='testdude',password='password')
        f.seek(0)
        response = c.post(submit_url, { 'photo': f, 'via': 'unit test', 'valid_check':True })
        self.failUnlessEqual(response.status_code, 201)
        #self.failUnlessEqual(response['Content-Type'],'application/json')
        # Ensure we have a proper user in the returned source
        obj = json.loads(response.content)
        self.assert_('source' in obj)
        self.assertEquals(obj['source']['name'], 'testdude')
        photo_comments_url = obj['comments']

        # Get the submit url again and make sure it has two submissions
        response = c.get(submit_url)
        self.failUnlessEqual(response.status_code,200)
        #self.failUnlessEqual(response['Content-Type'],'application/json')
        obj = json.loads(response.content)
        self.assertEquals(len(obj['submissions']),2)
        # Test the submissions URL
        response = c.get(obj['submissions'][0]['api_url'])
        self.failUnlessEqual(response.status_code,200)

        # We should now have a valid ballot
        response = c.get(ballot_url)
        self.failUnlessEqual(response.status_code,200)
        #self.failUnlessEqual(response['Content-Type'],'application/json')
        obj = json.loads(response.content)
        self.assertEquals(len(obj['submissions']),2)

        response = c.post(ballot_url, {'url':obj['submissions'][0]['url'] })
        # This should respond with a new ballot
        self.failUnlessEqual(response.status_code,200)
        #self.failUnlessEqual(response['Content-Type'],'application/json')

        # TODO: We also need some tests for:
        # Getting ballots and submitting votes for non-current hunts
        self.do_test_comment(c, hunt_comments_url, 'this is a hunt comment')
        self.do_test_comment(c, photo_comments_url, 'this is a photo comment')


    def do_test_comment(self, c, comments_url, comment_text):
        # Test comments
        # get hunt comments
        response = c.get(comments_url)
        self.failUnlessEqual(response.status_code,200)
        #self.failUnlessEqual(response['Content-Type'],'application/json')
        obj = json.loads(response.content)
        self.assertEquals(obj['comments'],[])
        # Add a comment
        response = c.post(comments_url, { 'text': comment_text })
        self.failUnlessEqual(response.status_code,201)
        #self.failUnlessEqual(response['Content-Type'],'application/json')
        the_comment_url = response['Content-Location']
        obj = json.loads(response.content)
        self.assertEquals(obj['text'], comment_text)
        self.assertEquals(obj['source']['name'], 'testdude')

        # retrieve the comment to make sure we get it back correctly
        response = c.get(the_comment_url)
        self.failUnlessEqual(response.status_code,200)
        #self.failUnlessEqual(response['Content-Type'],'application/json')
        obj = json.loads(response.content)
        self.assertEquals(obj['text'], comment_text)
        self.assertEquals(obj['source']['name'], 'testdude')

class CurrentHuntAPITest(TestCase):
    """
    Tests that current hunts include current and voting hunts
    """
    def setUp(self):
        self.user = User.objects.create_user('testdude','test@test.com','password')
        self.user.save()
        now = datetime.utcnow()
        self.hunts = [
            make_hunt(self.user, 'future hunt', 'future',   start=now + timedelta(1)),
            make_hunt(self.user, 'current hunt', 'current', start=now),
            make_hunt(self.user, 'voting hunt', 'voting',   start=now - timedelta(hours=2),
                           end_delta=timedelta(hours=1),
                           vote_delta=timedelta(hours=2)),
            make_hunt(self.user, 'finished hunt', 'finished', start=now - timedelta(hours=2),
                           end_delta=timedelta(hours=1))
        ]

    def tearDown(self):
        for h in self.hunts:
            h.delete()
        self.user.delete()

    def test_current(self):
        """
        Tests that current hunts include voting hunts
        """
        c = Client()
        response = c.get('/api/hunt/')
        self.failUnlessEqual(response.status_code,200)
        obj = json.loads(response.content)
        self.assert_(obj['hunts'])
        hunts = obj['hunts']
        self.assertEquals(len(hunts),4)

        response = c.get('/api/hunt/current/')
        self.failUnlessEqual(response.status_code,200)
        obj = json.loads(response.content)
        self.assert_(obj['hunts'])
        hunts = obj['hunts']
        self.assertEquals(len(hunts),2)


class LimitAPITest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('testdude','test@test.com','password')
        self.user.save()
        self.hunt = make_hunt(self.user,
                             'first test hunt',
                             'firsttest',
                             datetime.utcnow(),
                             vote_delta=timedelta(hours=1))

    def tearDown(self):
        self.hunt.delete()
        self.user.delete()

    def _newSubmission(self,c,submit_url,f):
        f.seek(0)
        response = c.post(submit_url, { 'photo': f, 'via': 'unit test' })
        self.failUnlessEqual(response.status_code, 201)
        return (response['Content-Location'],json.loads(response.content))

    def _newComment(self,c,comments_url,text):
        response = c.post(comments_url, { 'text': text })
        self.failUnlessEqual(response.status_code,201)

    def _getChildArray(self,c,url,array):
        response = c.get(url)
        self.failUnlessEqual(response.status_code,200)
        obj = json.loads(response.content)
        return obj[array]



    def test_limit(self):
        c = Client()
        c.login(username='testdude',password='password')
        response = c.get('/api/hunt/')
        self.failUnlessEqual(response.status_code,200)
        obj = json.loads(response.content)
        self.assert_(obj['hunts'])
        hunts = obj['hunts']
        self.assertEquals(len(hunts),1)
        # Follow the URLs and see what we get
        hunt = hunts[0]
        response = c.get(hunt['url'])
        self.failUnlessEqual(response.status_code,200)

        submit_url = hunt['submissions']
        hunt_comments_url = hunt['comments']

        f = testfiles.open_file('test1.jpg')
        photo1 = self._newSubmission(c,submit_url,f)
        photo2 = self._newSubmission(c,submit_url,f)
        photo3 = self._newSubmission(c,submit_url,f)

        # Get the submissions, there should be three
        submissions = self._getChildArray(c, submit_url, 'submissions')
        self.failUnlessEqual(len(submissions), 3)
        # Limit
        submissions = self._getChildArray(c, submit_url+"?limit=1", 'submissions')
        self.failUnlessEqual(len(submissions), 1)

        # Post a few comments (stagger them so we can predict their order)
        for t in ('one','two','three','four'):
            time.sleep(1)
            self._newComment(c,hunt_comments_url,t)

        comments = self._getChildArray(c, hunt_comments_url, 'comments')
        self.failUnlessEqual(len(comments), 4)
        # Limit
        comments = self._getChildArray(c, hunt_comments_url+"?limit=2", 'comments')
        self.failUnlessEqual(len(comments), 2)
        # Limit over how many there actually are
        comments = self._getChildArray(c, hunt_comments_url+"?limit=5", 'comments')
        self.failUnlessEqual(len(comments), 4)
        # Offset
        comments = self._getChildArray(c, hunt_comments_url+"?offset=1", 'comments')
        self.failUnlessEqual(len(comments), 3)
        self.failUnlessEqual(comments[0]['text'], 'three')
        self.failUnlessEqual(comments[1]['text'], 'two')
        self.failUnlessEqual(comments[2]['text'], 'one')
        # Offset off the end
        comments = self._getChildArray(c, hunt_comments_url+"?offset=5", 'comments')
        self.failUnlessEqual(len(comments), 0)
        # Offset + limit
        comments = self._getChildArray(c, hunt_comments_url+"?offset=2&limit=2", 'comments')
        self.failUnlessEqual(len(comments), 2)
        self.failUnlessEqual(comments[0]['text'], 'two')
        self.failUnlessEqual(comments[1]['text'], 'one')


class UserActivityAPITest(TestCase):
    def setUp(self):
        self.before = (datetime.utcnow() - timedelta(hours=1)).replace(tzinfo=pytz.utc)
        # Two users
        self.public_user = User.objects.create_user('publicguy','public@test.com','password')
        self.public_user.save()
        self.private_user = User.objects.create_user('privateguy', 'private@test.com', 'password')
        self.private_user.save()
        profile = self.private_user.get_profile()
        profile.public_activity=False
        profile.save()

        self.public_hunt = make_hunt(self.public_user,
                             'public test hunt',
                             'publictest',
                             datetime.utcnow(),
                             vote_delta=timedelta(hours=1))
        self.private_hunt = make_hunt(self.private_user,
                             'private test hunt',
                             'privatetest',
                             datetime.utcnow(),
                             vote_delta=timedelta(hours=1))

    def tearDown(self):
        self.public_hunt.delete()
        self.private_hunt.delete()
        self.public_user.delete()
        self.private_user.delete()

    def _newSubmission(self, c, hunt):
        f = testfiles.open_file('test1.jpg')
        response = c.post(hunt.get_submission_url(), { 'photo': f, 'via': 'unit test' })
        self.failUnlessEqual(response.status_code, 201)
        return json.loads(response.content)

    def _newComment(self, c, hunt, comment):
        response = c.post(hunt.get_comments_url(), { 'text': comment })
        self.failUnlessEqual(response.status_code, 201)
        return json.loads(response.content)

    def _newCommentUrl(self, c, url, comment):
        response = c.post(url, { 'text': comment })
        self.failUnlessEqual(response.status_code, 201)
        return json.loads(response.content)

    def _newVote(self, c, hunt, submission):
        response = c.post(hunt.get_ballot_url(), { 'url': submission })
        self.failUnlessEqual(response.status_code, 200)
        return json.loads(response.content)

    def _get(self, c, url, data={}):
        response = c.get(url, data)
        self.failUnlessEqual(response.status_code, 200)
        return json.loads(response.content)

    def test_user_activity(self):
        c = Client()
        # Add each type of object to each hunt and make sure it comes out correctly.
        c.login(username='publicguy',password='password')
        s1 = self._newSubmission(c, self.public_hunt)
        s2 = self._newSubmission(c, self.private_hunt)
        self._newComment(c, self.public_hunt, 'public guy on public hunt')
        self._newComment(c, self.private_hunt, 'public guy on private hunt')
        self._newCommentUrl(c, s1['comments'], 'public guy on s1')
        self._newCommentUrl(c, s2['comments'], 'public guy on s2')
        c.logout()

        c.login(username='privateguy',password='password')
        s3 = self._newSubmission(c, self.public_hunt)
        s4 = self._newSubmission(c, self.private_hunt)
        self._newComment(c, self.public_hunt, 'private guy on public hunt')
        self._newComment(c, self.private_hunt, 'private guy on private hunt')
        self._newCommentUrl(c, s3['comments'], 'private guy on s3')
        self._newCommentUrl(c, s4['comments'], 'private guy on s4')
        c.logout()

        c.login(username='publicguy',password='password')
        self._newVote(c, self.public_hunt, s1['url'])
        self._newVote(c, self.private_hunt, s2['url'])
        c.logout()

        c.login(username='privateguy',password='password')
        self._newVote(c, self.public_hunt, s3['url'])
        self._newVote(c, self.private_hunt, s4['url'])
        c.logout()

        public_json = self._get(c, '/api/user/publicguy/')
        private_json = self._get(c, '/api/user/privateguy/')
        public_activity_url = public_json['activity']
        private_activity_url = private_json['activity']

        # Currently we are logged in as no one
        # Get the public guy's activity
        public_activity = self._get(c, public_activity_url)
        self.assert_(public_activity['activity'])
        # TODO: test more on this
        #print public_activity
        # private guy should be inaccessible
        response = c.get(private_activity_url)
        self.failUnlessEqual(response.status_code, 403)

        EXPECTED = 8
        # Log in as public guy, it should be the same
        c.login(username='publicguy',password='password')
        public_activity = self._get(c, public_activity_url)
        self.assert_(public_activity['activity'])
        # One hunt, two submissions, two comments, two (=one) vote
        self.failUnlessEqual(len(public_activity['activity']), EXPECTED)
        # private guy should be inaccessible
        response = c.get(private_activity_url)
        self.failUnlessEqual(response.status_code, 403)
        c.logout()

        # Log in as private guy, both should be available
        c.login(username='privateguy',password='password')
        public_activity = self._get(c, public_activity_url)
        self.assert_(public_activity['activity'])
        private_activity = self._get(c, private_activity_url)
        self.assert_(private_activity['activity'])
        self.failUnlessEqual(len(private_activity['activity']), EXPECTED)
        c.logout()

        total_len = len(public_activity['activity'])
        # Test since YYYY-MM-DDTHH:MM:SS.mmmmmm
        # the logic for determining what is returned is tested at the model layer,
        # so we are mainly just testing the argument and its parsing
        since = self.before.isoformat()
        activity = self._get(c, public_activity_url, data={'since': since})
        self.failUnlessEqual(len(activity['activity']), EXPECTED)

        # We can't necessarily test the order (since we added them too quickly)
        # But we can test a few things that should be there
        self.failUnlessEqual(activity['user']['name'], 'publicguy')
        for a in activity['activity']:
            self.assert_(a['type'])
            self.assert_(a['time'])
            self.assert_(a['hunt'])
            t = a['type']
            if t == "submission" or t == "award":
                self.assert_(a['submission'])
            if t == "comment":
                self.assert_('submission' in a or 'hunt' in a)

        future = (self.before + timedelta(hours=2)).isoformat()
        activity = self._get(c, public_activity_url, data={'since': future})
        self.failUnlessEqual(len(activity['activity']), 0)

__test__ = {}

