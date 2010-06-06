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

from gonzo.hunt.models import *
from gonzo.hunt import testfiles
from gonzo.hunt import game

def make_hunt(user, phrase, tag, start, end_delta=timedelta(hours=1), vote_delta=None):
    end = start + end_delta
    if vote_delta:
        vote = end + vote_delta
    else:
        vote = end
    h = Hunt(owner=user, phrase=phrase, tag=tag, start_time=start, end_time=end, vote_end_time=vote)
    h.save()
    return h

def make_submission(hunt, path, **kwargs):
    s = Submission(hunt=hunt, ip_address='127.0.0.1', via='unit test', **kwargs)
    s.photo.file = File(testfiles.get_file_path(path))
    s.photo_width = 2048
    s.photo_height = 1536
    s.save()
    return s


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
        h = Hunt()
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
        self.assertEquals(future.get_state(), Hunt.State.FUTURE)

        current = make_hunt(self.user,
                        'current hunt',
                        'current',
                        now)
        self.assertEquals(current.get_state(), Hunt.State.CURRENT)

        voting = make_hunt(self.user,
                           'voting hunt',
                           'voting',
                           start=now - timedelta(hours=2),
                           end_delta=timedelta(hours=1),
                           vote_delta=timedelta(hours=2))
        self.assertEquals(voting.get_state(), Hunt.State.VOTING)

        finished = make_hunt(self.user,
                             'finished hunt',
                             'finished',
                             start=now - timedelta(hours=2),
                             end_delta=timedelta(hours=1))
        self.assertEquals(finished.get_state(), Hunt.State.FINISHED)

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
        s1 = make_submission(self.hunt, 'test1,jpg', user=self.user)
        time.sleep(1)
        s2 = make_submission(self.hunt, 'test1.jpg', anon_source='twitter:joulespersecond')
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
        self.submission = make_submission(self.hunt, 'test1.jpg', user=self.user)

    def tearDown(self):
        self.submission.delete()
        self.hunt.delete()
        self.user.delete()

    def _newComment(self, text, **kwargs):
        return Comment.objects.create(hunt=self.hunt, text=text, ip_address='127.0.0.1', **kwargs)

    def test_hunt_order(self):
        # Make two comments on the hunt, separated by a second or so
        hunt1 = self._newComment('Comment 1', user=self.user)
        time.sleep(1)
        hunt2 = self._newComment('Comment 2', anon_source='twitter:joulespersecond')
        self.assertEquals(self.hunt.comment_set.count(), 2)
        # Make sure 'Comment 2' is first
        self.assertEquals(self.hunt.comment_set.all()[0].text, 'Comment 2')
        self.assertEquals(self.hunt.comment_set.all()[1].text, 'Comment 1')

        s1 = self._newComment('Photo Comment 1',
                              submission=self.submission,
                              user=self.user)
        time.sleep(1)
        s2 = self._newComment('Photo Comment 2',
                              submission=self.submission,
                              anon_source='twitter:joulespersecond')
        self.assertEquals(self.submission.comment_set.count(), 2)
        # Make sure 'comment 2' is first
        self.assertEquals(self.submission.comment_set.all()[0].text, 'Photo Comment 2')
        self.assertEquals(self.submission.comment_set.all()[1].text, 'Photo Comment 1')
        # There should be 4 hunt comments how
        self.assertEquals(self.hunt.comment_set.count(), 4)
        # To get all the non-submission hunts
        self.assertEquals(self.hunt.comment_set.filter(submission=None).count(), 2)


class AssignAwardsTest(TestCase):
    def setUp(self):
        self.users = [
             User.objects.create_user('testdude0','test0@test.com','password'),
             User.objects.create_user('testdude1','test1@test.com','password'),
             User.objects.create_user('testdude2','test2@test.com','password'),
             User.objects.create_user('testdude3','test3@test.com','password'),
             User.objects.create_user('testdude4','test4@test.com','password')
        ]
        for u in self.users:
            u.save()
        self.hunt = make_hunt(self.users[0],
                              'assign awards',
                              'awards',
                              start=datetime.utcnow() - timedelta(hours=2))
        self.submissions = [
            make_submission(self.hunt, 'test1.jpg', user=self.users[0]),
            make_submission(self.hunt, 'test1.jpg', user=self.users[1]),
            make_submission(self.hunt, 'test1.jpg', user=self.users[2]),
            make_submission(self.hunt, 'test1.jpg', user=self.users[3]),
            make_submission(self.hunt, 'test1.jpg', user=self.users[4]),
        ]

    def tearDown(self):
        self.hunt.delete()
        for u in self.users:
            u.delete()

    def _castVotes(self, votes):
        """Votes are specified as (user, submission, value)"""
        for v in votes:
            Vote.objects.create(hunt=self.hunt,
                                user=self.users[v[0]],
                                submission=self.submissions[v[1]],
                                value=v[2],
                                ip_address='127.0.0.1')

    def _checkAward(self,award,winners):
        entries = Award.objects.filter(hunt=self.hunt,value=award)
        self.assertEquals(winners, [e.submission for e in entries])

    def _checkAwards(self, gold, silver, bronze):
        """
        Parameters are lists or tuples of the submission indexes that won.
        We translate that into submissions
        """
        self._checkAward(Award.GOLD, [self.submissions[i] for i in gold])
        self._checkAward(Award.SILVER, [self.submissions[i] for i in silver])
        self._checkAward(Award.BRONZE, [self.submissions[i] for i in bronze])

    def test_1_simple(self):
        self._castVotes([
            # user, submission, value
            (0, 0, 1),
            (1, 1, 2),
            (2, 2, 3)
        ])
        game.assign_awards()
        self._checkAwards((2,), (1,), (0,))

    def test_2_no_bronze(self):
        self._castVotes([
            # user, submission, value
            (0, 0, 1),
            (0, 0, 1),
            (1, 1, 1),
        ])
        game.assign_awards()
        self._checkAwards((0,), (1,), ())

    def test_3_no_silver(self):
        self._castVotes([
            # user, submission, value
            (0, 0, 1),
        ])
        game.assign_awards()
        self._checkAwards((0,), (), ())

    def test_4_none(self):
        game.assign_awards()
        self._checkAwards((), (), ())

    def test_5_shared_gold(self):
        self._castVotes([
            # user, submission, value
            (0, 0, 1),
            (1, 1, 2),
            (2, 1, 2),
            (1, 2, 2),
            (2, 2, 2)
        ])
        game.assign_awards()
        self._checkAwards((1,2), (0,), ())

    def test_6_shared_gold_silver(self):
        self._castVotes([
            # user, submission, value
            (0, 0, 2), # 0 has 2
            (1, 1, 2),
            (1, 1, 2), # 1 has 4
            (1, 2, 2),
            (2, 2, 2), # 2 has 4
            (3, 3, 3),
            (3, 3, 3), # 3 has 6
            (0, 4, 3),
            (1, 4, 3)  # 4 has 6
        ])
        game.assign_awards()
        self._checkAwards((3,4), (1,2), ())

    def test_7_shared_gold(self):
        self._castVotes([
            # user, submission, value
            (0, 0, 4),
            (1, 0, 4), # 0 has 8
            (1, 1, 2),
            (1, 1, 2),
            (1, 1, 4), # 1 has 8
            (1, 2, 4),
            (2, 2, 4), # 2 has 8
            (3, 3, 3),
            (3, 3, 3), # 3 has 6
            (0, 4, 3),
            (1, 4, 3)  # 4 has 6
        ])
        game.assign_awards()
        self._checkAwards((0,1,2), (), ())

    def test_8_shared_bronze(self):
        self._castVotes([
            # user, submission, value
            (0, 0, 1),
            (1, 0, 1), # 0 has 2
            (1, 1, 2),
            (1, 1, 2), # 1 has 4
            (1, 2, 1),
            (2, 2, 1), # 2 has 2
            (3, 3, 3),
            (3, 3, 3), # 3 has 6
            (0, 4, 1),
            (1, 4, 1)  # 4 has 2
        ])
        game.assign_awards()
        self._checkAwards((3,), (1,), (0,2,4))

class DeleteUnplayedTest(TestCase):
    def setUp(self):
        self.hunts = []
        self.user = User.objects.create_user('testdude','test@test.com','password')

    def tearDown(self):
        for h in self.hunts:
            h.delete()
        self.user.delete()

    def new_used_past(self):
        start = datetime.utcnow() - timedelta(hours=3)
        hunt = make_hunt(self.user, 'new used past', 'usedpast', start)
        sub = make_submission(hunt, 'test1.jpg', user=self.user)
        vote = Vote.objects.create(hunt=hunt,
                                   user=self.user,
                                   submission=sub,
                                   value=1,
                                   ip_address='127.0.0.1')
        self.hunts.append(hunt)
        return hunt

    def new_unused_past(self):
        start = datetime.utcnow() - timedelta(hours=3)
        hunt = make_hunt(self.user, 'new unused past', 'unusedpast', start)
        self.hunts.append(hunt)
        return hunt

    def new_used_current(self):
        start = datetime.utcnow() - timedelta(minutes=5)
        hunt = make_hunt(self.user, 'new used current', 'usedcurrent', start)
        sub = make_submission(hunt, 'test1.jpg', user=self.user)
        vote = Vote.objects.create(hunt=hunt,
                                   user=self.user,
                                   submission=sub,
                                   value=1,
                                   ip_address='127.0.0.1')
        self.hunts.append(hunt)
        return hunt

    def new_unused_current(self):
        start = datetime.utcnow() - timedelta(minutes=5)
        hunt = make_hunt(self.user, 'new unused past', 'unusedpast', start)
        self.hunts.append(hunt)
        return hunt

    def _doTest(self, before, after):
        self.assertEquals(Hunt.objects.count(), before)
        game.delete_unplayed()
        self.assertEquals(Hunt.objects.count(), after)

    def test_1(self):
        self.new_unused_past()
        self._doTest(1, 0)

    def test_2(self):
        # One used, one unused.
        self.new_unused_past()
        self.new_used_past()
        self._doTest(2, 1)

    def test_3(self):
        self.new_unused_past()
        self.new_unused_current()
        self._doTest(2, 1)

    def test_4(self):
        self.new_used_current()
        self._doTest(1, 1)

    def test_5(self):
        self.new_used_past()
        self.new_unused_current()
        self._doTest(2, 2)

    def test_6(self):
        self.new_unused_past()
        self.new_unused_current()
        self.new_unused_past()
        self._doTest(3, 1)

class KeepActiveTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('testdude','test@test.com','password')

    def tearDown(self):
        self.user.delete()

    def test_keep_active(self):
        game.keep_active(self.user.username, timedelta(hours=1))
        self.assertEquals(Hunt.objects.count(),1)
        game.keep_active(self.user.username, timedelta(hours=1))
        self.assertEquals(Hunt.objects.count(),1)

__test__ = {}

