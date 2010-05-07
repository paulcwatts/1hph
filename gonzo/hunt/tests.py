"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""
import json
from datetime import datetime, timedelta

from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User

from gonzo.hunt import models

def make_hunt(user, phrase, tag, start, end_delta=timedelta(hours=1), vote_delta=None):
    end = start + end_delta
    if vote_delta:
        vote = end + vote_delta
    else:
        vote = end
    h = models.Hunt(owner=user,
                    phrase=phrase,
                    tag=tag,
                    start_time=start,
                    end_time=end,
                    vote_end_time=vote)
    h.save()
    return h;

class HuntModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('testdude','test@test.com','password')
        self.user.save()

    def tearDown(self):
        self.user.delete()

    def test_slug(self):
        h1 = make_hunt(self.user,
                       'first test hunt',
                       'firsttest',
                       datetime.utcnow(),
                       vote_delta=timedelta(hours=1))
        self.assertEquals(h1.slug, 'first-test-hunt')
        # Make sure we can save again and the slug stays the same
        h1.max_submissions = 100
        h1.save()
        self.assertEquals(h1.slug, 'first-test-hunt')
        # Create a new one with the same phrase, ensure the slug changes
        h2 = make_hunt(self.user,
                       'first test hunt',
                       'firsttest2',
                       datetime.utcnow(),
                       vote_delta=timedelta(hours=1))
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
        h.start_time = datetime.utcnow()
        h.end_time = h.start_time
        h.vote_end_time = h.end_time
        self.failUnlessRaises(ValidationError, lambda: h.save())
        h.start_time = datetime.utcnow()
        h.end_time = h.start_time - timedelta(seconds=1)
        h.vote_end_time = h.end_time
        self.failUnlessRaises(ValidationError, lambda: h.save())
        h.start_time = datetime.utcnow()
        h.end_time = h.end_time + timedelta(hours=1)
        h.vote_end_time = h.end_time - timedelta(minutes=1)
        self.failUnlessRaises(ValidationError, lambda: h.save())
        h.vote_end_time = h.end_time
        h.save()

    def test_state(self):
        now = datetime.utcnow()
        future = make_hunt(self.user,
                       'future hunt',
                       'future',
                       now + timedelta(1))
        self.assertEquals(future.get_state(), models.Hunt.State.FUTURE)

        current = make_hunt(self.user,
                        'current hunt',
                        'current',
                        now)
        self.assertEquals(current.get_state(), models.Hunt.State.CURRENT)

        voting = make_hunt(self.user,
                           'voting hunt',
                           'voting',
                           start=now - timedelta(hours=2),
                           end_delta=timedelta(hours=1),
                           vote_delta=timedelta(hours=2))
        self.assertEquals(voting.get_state(), models.Hunt.State.VOTING)

        finished = make_hunt(self.user,
                             'finished hunt',
                             'finished',
                             start=now - timedelta(hours=2),
                             end_delta=timedelta(hours=1))
        self.assertEquals(finished.get_state(), models.Hunt.State.FINISHED)


__test__ = {}

