"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase
from gonzo.hunt import models
from datetime import datetime, timedelta
from django.contrib.auth.models import User

class HuntModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('testdude','test@test.com','password')
        self.user.save()

    def tearDown(self):
        self.user.delete()

    def test_slug(self):
        h1 = models.Hunt()
        h1.owner = self.user
        h1.phrase = 'first test hunt'
        h1.tag = 'firsttest'
        h1.start_time = datetime.now()
        h1.end_time = h1.start_time + timedelta(hours=1)
        h1.vote_end_time = h1.end_time + timedelta(hours=1)
        h1.save()
        self.assertEquals(h1.slug, 'first-test-hunt')
        # Make sure we can save again and the slug stays the same
        h1.max_submissions = 100
        h1.save()
        self.assertEquals(h1.slug, 'first-test-hunt')
        # Create a new one with the same phrase, ensure the slug changes
        h2 = models.Hunt()
        h2.owner = self.user
        h2.phrase = 'first test hunt'
        h2.tag = 'firsttest2'
        h2.start_time = datetime.now()
        h2.end_time = h2.start_time + timedelta(hours=1)
        h2.vote_end_time = h2.end_time + timedelta(hours=1)
        h2.save()
        self.assertEquals(h2.slug, 'first-test-hunt-1')
        h2.max_submissions = 100
        h2.save()
        self.assertEquals(h2.slug, 'first-test-hunt-1')

    def test_validation(self):
        from django.core.exceptions import ValidationError
        h = models.Hunt()
        h.owner = self.user
        h.phrase = 'not valid hunt'
        h.tag = 'notvalid'
        h.start_time = datetime.now()
        h.end_time = h.start_time
        h.vote_end_time = h.end_time
        self.failUnlessRaises(ValidationError, lambda: h.save())
        h.start_time = datetime.now()
        h.end_time = h.start_time - timedelta(seconds=1)
        h.vote_end_time = h.end_time
        self.failUnlessRaises(ValidationError, lambda: h.save())
        h.start_time = datetime.now()
        h.end_time = h.end_time + timedelta(hours=1)
        h.vote_end_time = h.end_time - timedelta(minutes=1)
        self.failUnlessRaises(ValidationError, lambda: h.save())
        h.vote_end_time = h.end_time
        h.save()



__test__ = {}

