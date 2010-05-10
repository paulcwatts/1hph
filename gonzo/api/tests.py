"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""
import json, time
import StringIO
from datetime import datetime, timedelta

from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User

from gonzo.hunt import models
from gonzo.hunt.tests import make_hunt
from gonzo.hunt import testfiles

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


__test__ = {}

