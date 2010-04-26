"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""
import json

from django.test import TestCase
from django.test.client import Client
from gonzo.hunt import models
from datetime import datetime, timedelta
from django.contrib.auth.models import User

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
        response = c.get(hunt['submissions'])
        self.failUnlessEqual(response.status_code,200)
        self.failUnlessEqual(response['Content-Type'],'application/json')
        # No submissions yet
        obj = json.loads(response.content)
        self.assertEquals(obj['submissions'],[])


__test__ = {}

