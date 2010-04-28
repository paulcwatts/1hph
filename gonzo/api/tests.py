"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""
import json
import StringIO

from django.test import TestCase
from django.test.client import Client
from gonzo.hunt import models
from datetime import datetime, timedelta
from django.contrib.auth.models import User

class StringFile(StringIO.StringIO):
    def __init__(self,name,buffer):
        self.name = name
        #super(StringFile,self).__init__(buffer)
        StringIO.StringIO.__init__(self,buffer)

class HuntAPITest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('testdude','test@test.com','password')
        self.user.save()
        h1 = models.Hunt()
        h1.owner = self.user
        h1.phrase = 'first test hunt'
        h1.tag = 'firsttest'
        h1.start_time = datetime.now()
        h1.end_time = h1.start_time + timedelta(hours=1)
        h1.vote_end_time = h1.end_time + timedelta(hours=1)
        h1.save()
        self.hunt = h1

    def tearDown(self):
        self.hunt.delete()
        self.user.delete()

    def test_API(self):
        c = Client()
        response = c.get('/api/hunt/')
        self.failUnlessEqual(response.status_code,200)
        self.failUnlessEqual(response['Content-Type'],'application/json')
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
        self.failUnlessEqual(response['Content-Type'],'application/json')
        # No submissions yet
        obj = json.loads(response.content)
        self.assertEquals(obj['submissions'],[])

        from StringIO import StringIO
        # TODO: Test submssion -- authenticated and anonymous
        # photo, latitude, longitude, source_via
        # First test an invalid file
        import os.path
        path = os.path.abspath(os.path.dirname(__file__))
        response = c.post(submit_url, { 'photo':
                                      StringFile("testfile.txt","This is an invalid photo"),
                                      'source_via': 'unit test' })
        self.failUnlessEqual(response.status_code, 400)
        f = open(os.path.join(path,'testfiles/test1.jpg'))
        response = c.post(submit_url, { 'photo': f, 'via': 'unit test' })
        self.failUnlessEqual(response.status_code, 201)
        self.failUnlessEqual(response['Content-Type'],'application/json')
        photo1Url = response['Content-Location']

         # Ensure that the ballot url returns an error
        response = c.get(ballot_url)
        self.failUnlessEqual(response.status_code,400)

        # Now log in and submit a photo
        c.login(username='testdude',password='password')
        f.seek(0)
        response = c.post(submit_url, { 'photo': f, 'via': 'unit test' })
        self.failUnlessEqual(response.status_code, 201)
        self.failUnlessEqual(response['Content-Type'],'application/json')
        # Ensure we have a proper user in the returned source
        obj = json.loads(response.content)
        self.assert_('source' in obj)
        self.assertEquals(obj['source']['name'], 'testdude')
        photo_comments_url = obj['comments']

        # Get the submit url again and make sure it has two submissions
        response = c.get(submit_url)
        self.failUnlessEqual(response.status_code,200)
        self.failUnlessEqual(response['Content-Type'],'application/json')
        obj = json.loads(response.content)
        self.assertEquals(len(obj['submissions']),2)

        # We should now have a valid ballot
        response = c.get(ballot_url)
        self.failUnlessEqual(response.status_code,200)
        self.failUnlessEqual(response['Content-Type'],'application/json')
        obj = json.loads(response.content)
        self.assertEquals(len(obj['submissions']),2)

        response = c.post(ballot_url, {'url':obj['submissions'][0]['url'] })
        # This should respond with a new ballot
        self.failUnlessEqual(response.status_code,200)
        self.failUnlessEqual(response['Content-Type'],'application/json')

        # TODO: We also need some tests for:
        # Getting ballots and submitting votes for non-current hunts
        self.do_test_comment(c, hunt_comments_url, 'this is a hunt comment')
        self.do_test_comment(c, photo_comments_url, 'this is a photo comment')


    def do_test_comment(self, c, comments_url, comment_text):
        # Test comments
        # get hunt comments
        response = c.get(comments_url)
        self.failUnlessEqual(response.status_code,200)
        self.failUnlessEqual(response['Content-Type'],'application/json')
        obj = json.loads(response.content)
        self.assertEquals(obj['comments'],[])
        # Add a comment
        response = c.post(comments_url, { 'text': comment_text })
        self.failUnlessEqual(response.status_code,201)
        self.failUnlessEqual(response['Content-Type'],'application/json')
        the_comment_url = response['Content-Location']
        obj = json.loads(response.content)
        self.assertEquals(obj['text'], comment_text)
        self.assertEquals(obj['source']['name'], 'testdude')

        # retrieve the comment to make sure we get it back correctly
        response = c.get(the_comment_url)
        self.failUnlessEqual(response.status_code,200)
        self.failUnlessEqual(response['Content-Type'],'application/json')
        obj = json.loads(response.content)
        self.assertEquals(obj['text'], comment_text)
        self.assertEquals(obj['source']['name'], 'testdude')


__test__ = {}

