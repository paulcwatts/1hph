from datetime import datetime, timedelta
import pytz

from django.test import TestCase
from django.core.files import File

from gonzo.hunt.models import *
from gonzo.hunt import testfiles
from gonzo.account.models import user_activity

class UserActivityTest(TestCase):
    start_time = datetime(2010, 5, 5, 8, 0, 0)

    def setUp(self):
        self.user = User.objects.create_user('testdude','test@test.com','password')
        self.user.save()

    def tearDown(self):
        self.user.delete()

    def _newHunt(self, phrase, start_time):
        return Hunt.objects.create(owner=self.user,
                    phrase=phrase,
                    tag='test',
                    create_time=start_time,
                    start_time=start_time,
                    end_time=start_time + timedelta(hours=1),
                    vote_end_time=start_time + timedelta(hours=1))

    def _newSubmission(self, hunt, delta):
        submission = Submission(hunt=hunt,
                                 user=self.user,
                                 time=hunt.start_time+delta,
                                 ip_address='127.0.0.1',
                                 via='unit test')
        submission.photo.file = File(testfiles.get_file_path('test1.jpg'))
        submission.photo_width = 2048
        submission.photo_height = 1536
        submission.save()
        return submission

    def _newVote(self,hunt,submission,delta):
        return Vote.objects.create(hunt=hunt,
                                   submission=submission,
                                   time=hunt.start_time+delta,
                                   value=1,
                                   user=self.user,
                                   ip_address='127.0.0.1')

    def test_activity(self):
        # Create a hunt
        #
        hunt1 = self._newHunt('test one phrase', self.start_time)
        sub1 = self._newSubmission(hunt1, timedelta(minutes=15))

        hunt2_time = self.start_time + timedelta(minutes=30)
        hunt2 = self._newHunt('test two phrase', hunt2_time)
        activity = user_activity(self.user)
        self.failUnlessEqual(activity,[hunt2,sub1,hunt1])

        activity = user_activity(self.user, self.start_time+timedelta(minutes=14))
        self.failUnlessEqual(activity,[hunt2,sub1])

        activity = user_activity(self.user, self.start_time+timedelta(minutes=29))
        self.failUnlessEqual(activity,[hunt2])

        sub2 = self._newSubmission(hunt1, timedelta(minutes=20))
        # Add some votes
        v1 = self._newVote(hunt1, sub1, timedelta(minutes=21))
        v2 = self._newVote(hunt1, sub1, timedelta(minutes=45))
        v3 = self._newVote(hunt1, sub2, timedelta(minutes=46))

        # What it would be: [v3,v2,hunt2,v1,sub2,sub1,hunt1]
        activity = user_activity(self.user)
        self.failUnlessEqual(activity,[v3,hunt2,v1,sub2,sub1,hunt1])

        activity = user_activity(self.user, self.start_time+timedelta(minutes=45,seconds=30))
        self.failUnlessEqual(activity,[v3])

        activity = user_activity(self.user, self.start_time+timedelta(minutes=50))
        self.failUnlessEqual(activity,[])

__test__ = {}

