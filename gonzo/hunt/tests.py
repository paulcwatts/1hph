"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""
import json, time
from datetime import datetime, timedelta

from django.core.files import File
from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User

from gonzo.hunt import models
from gonzo.hunt import testfiles

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
    return h

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

class SubmitTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('testdude','test@test.com','password')
        self.user.save()
        # Create a hunt
        self.hunt = make_hunt(self.user,
                              'my submit hunt',
                              'submithunt',
                              start=datetime.utcnow())

    def tearDown(self):
        self.hunt.delete()
        self.user.delete()

    def test_order(self):
        s1 = models.Submission(hunt=self.hunt,
                               user=self.user,
                               ip_address='127.0.0.1',
                               via='unit test')
        s1.photo.file = File(testfiles.get_file_path('test1.jpg'))
        s1.photo_width = 2048
        s1.photo_height = 1536
        s1.save()

        time.sleep(1)
        s2 = models.Submission(hunt=self.hunt,
                                anon_source='twitter:joulespersecond',
                                ip_address='127.0.0.1',
                                via='unit test')
        s2.photo.file = File(testfiles.get_file_path('test1.jpg'))
        s2.photo_width = 2048
        s2.photo_height = 1536
        s2.save()

        self.assertEquals(self.hunt.submission_set.count(), 2)
        # The anonymous one should be first
        self.assertEquals(self.hunt.submission_set.all()[0].anon_source, 'twitter:joulespersecond')
        self.assertEquals(self.hunt.submission_set.all()[1].user, self.user)


class CommentTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('testdude','test@test.com','password')
        self.user.save()
        # Create a hunt
        self.hunt = make_hunt(self.user,
                              'my comment hunt',
                              'commenthunt',
                              start=datetime.utcnow())
        self.submission = models.Submission(hunt=self.hunt,
                                     user=self.user,
                                     ip_address='127.0.0.1',
                                     via='unit test')
        self.submission.photo.file = File(testfiles.get_file_path('test1.jpg'))
        self.submission.photo_width = 2048
        self.submission.photo_height = 1536
        self.submission.save()

    def tearDown(self):
        self.submission.delete()
        self.hunt.delete()
        self.user.delete()

    def test_hunt_order(self):
        # Make two comments on the hunt, separated by a second or so
        hunt1 = models.Comment.objects.create(hunt=self.hunt,
                                   user=self.user,
                                   text='Comment 1',
                                   ip_address='127.0.0.1')

        time.sleep(1)
        hunt2 = models.Comment.objects.create(hunt=self.hunt,
                                    anon_source='twitter:joulespersecond',
                                    text='Comment 2',
                                    ip_address='127.0.0.1')
        self.assertEquals(self.hunt.comment_set.count(), 2)
        # Make sure 'Comment 2' is first
        self.assertEquals(self.hunt.comment_set.all()[0].text, 'Comment 2')
        self.assertEquals(self.hunt.comment_set.all()[1].text, 'Comment 1')

        s1 = models.Comment.objects.create(hunt=self.hunt,
                                   submission=self.submission,
                                   user=self.user,
                                   text='Photo Comment 1',
                                   ip_address='127.0.0.1')

        time.sleep(1)
        s2 = models.Comment.objects.create(hunt=self.hunt,
                                    submission=self.submission,
                                    anon_source='twitter:joulespersecond',
                                    text='Photo Comment 2',
                                    ip_address='127.0.0.1')
        self.assertEquals(self.submission.comment_set.count(), 2)
        # Make sure 'comment 2' is first
        self.assertEquals(self.submission.comment_set.all()[0].text, 'Photo Comment 2')
        self.assertEquals(self.submission.comment_set.all()[1].text, 'Photo Comment 1')
        # There should be 4 hunt comments how
        self.assertEquals(self.hunt.comment_set.count(), 4)
        # To get all the non-submission hunts
        self.assertEquals(self.hunt.comment_set.filter(submission=None).count(), 2)


__test__ = {}

