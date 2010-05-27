from StringIO import StringIO
import time
from datetime import datetime, timedelta
from email.utils import formatdate

from django.core.files import File
from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User

from gonzo.hunt.models import *
from gonzo.hunt.tests import make_hunt
from gonzo.connectors import email

TESTEMAIL="""From paulcwatts@gmail.com  Thu May 27 21:53:10 2010
From: %(from)s
Content-Type: multipart/mixed; boundary=Apple-Mail-6-337242388
Subject: %(subject)s
Message-Id: <0C017C7D-2FB6-4EF1-8DFC-BB2D4DAFE313@gmail.com>
Date: %(date)s
To: %(to)s


--Apple-Mail-6-337242388
Content-Transfer-Encoding: 7bit
Content-Type: text/plain;
    charset=us-ascii

this is a test

--Apple-Mail-6-337242388
Content-Disposition: inline;
    filename=testsmall.jpg
Content-Type: image/jpg;
    x-unix-mode=0755;
    name="testsmall.jpg"
Content-Transfer-Encoding: base64

/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0a
HBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIy
MjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAC0APADASIA
AhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQA
AAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3
ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWm
p6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEA
AwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSEx
BhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElK
U1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3
uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwDjo7m5
tdXkW1cIXwysRng8f1qmLeYJeQTffXPPrg//AK6mkylxZy8BipjP1BxU9zKr30kqBpBMv3V6ksuP
55rpklL3u/6oya5G4drr7mS+FpxDrcJJGGaNv6H+VbF4g/s2+hBBMRkU+xU5/pXLaQ7R31sw4wCP
yYH+tdldxg6rqaYIM58xhjj5lH+P6VjiI6wqdmP7Fjlr/d58pXbuZkYZ6fMMVNan91A3oP5VDcNl
IZSODAh4/wBkipLQ5t1yCCGIweooxKtN+p9JlEuaKXeP5No6QLjxjCcY86Ij81rHht2KSukLkRE7
nU8Dk9eK0I5iPEGkSk5G9UJ/D/69aFlpBm/tBWedEVpcbT8pwc4NFWPMeZgK8cPJxl6fjYi0jjxj
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
iipBjwxGfrVHWEU2gYjn1ooqo7kT2P/Z

--Apple-Mail-6-337242388--

"""
NOT_MULTIPART="""From paulcwatts@gmail.com  Thu May 27 20:57:30 2010
From: Paul Watts <paulcwatts@gmail.com>
Content-Type: text/plain; charset=us-ascii
Content-Transfer-Encoding: 7bit
Subject: This is a test
Date: Thu, 27 May 2010 13:57:27 -0700
Message-Id: <0C017C7D-2FB6-4EF1-8DFC-BB2D4DAFE313@gmail.com>
To: hunt+huntname@1hph.com


Can we read this file?

"""

NOT_AN_IMAGE="""From paulcwatts@gmail.com  Thu May 27 23:42:09 2010
From: Paul Watts <paulcwatts@gmail.com>
Content-Type: multipart/mixed; boundary=Apple-Mail-7-343782664
Subject: not an image
Message-Id: <7004111D-00B2-41B6-B1C1-542B67A6FF17@gmail.com>
To: hunt+huntname@1hph.com
Mime-Version: 1.0 (Apple Message framework v1078)
X-Mailer: Apple Mail (2.1078)


--Apple-Mail-7-343782664
Content-Disposition: attachment;
    filename=notanimage.rtf
Content-Type: %(content_type)s;
    x-mac-hide-extension=yes;
    x-unix-mode=0644;
    name="notanimage.rtf"
Content-Transfer-Encoding: 7bit

{\rtf1\ansi\ansicpg1252\cocoartf1038\cocoasubrtf290
{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
\margl1440\margr1440\vieww9000\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\ql\qnatural\pardirnatural

\f0\fs24 \cf0 This is not an image}
--Apple-Mail-7-343782664--

"""


class EmailTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('testdude','test@test.com','password')
        self.user.save()
        # Create a hunt
        self.hunt = make_hunt(self.user, 'test email hunt', 'emailtest', datetime.utcnow())

    def tearDown(self):
        self.user.delete()
        self.hunt.delete()

    #
    # Test cases:
    # Valid from:
    #    Anonymous submission
    #        (handle addy's of the form "Real Name <email@domain.com>"
    #    User submission (recognized email address)
    #        (handle addy's of the form "Real Name <email@domain.com>"
    # Invalid from:
    #    Reject
    #
    # We *should* be able to send everything through the API.
    #
    # Hunt exists
    # Hunt doesn't exist, or isn't current.
    #
    #

    def test_0_submit_anon(self):
        now = time.mktime(time.gmtime())
        msg = TESTEMAIL % { 'from': 'paulwfoo@test.com',
            'to': 'hunt+emailtest@1hph.com',
            'subject': 'test 1',
            'date': formatdate(now) }
        environ = { 'RECIPIENT': 'hunt+emailtest@1hph.com', 'SENDER': 'paulw@test.com' }
        submission = email.submit_from_file(environ, StringIO(msg))
        self.assert_(submission)
        self.assertEquals(submission.user, None)
        self.assertEquals(submission.hunt, self.hunt)
        self.assert_(submission.photo)
        self.assertEquals(submission.photo_width, 240)
        self.assertEquals(submission.photo_height, 180)
        self.assertEquals(submission.anon_source, 'email:name=&addr=paulw%40test.com')
        self.assertEquals(submission.via, 'email')

    def test_1_submit_anon(self):
        now = time.mktime(time.gmtime())
        msg = TESTEMAIL % { 'from': 'Paul Watts <paulwfoo@test.com>',
            'to': 'hunt+emailtest@1hph.com',
            'subject': 'test 1',
            'date': formatdate(now) }
        environ = { 'RECIPIENT': 'hunt+emailtest@1hph.com', 'SENDER': 'paulw@test.com' }
        submission = email.submit_from_file(environ, StringIO(msg))
        self.assert_(submission)
        self.assertEquals(submission.user, None)
        self.assertEquals(submission.hunt, self.hunt)
        self.assert_(submission.photo)
        self.assertEquals(submission.photo_width, 240)
        self.assertEquals(submission.photo_height, 180)
        self.assertEquals(submission.anon_source, 'email:name=Paul+Watts&addr=paulw%40test.com')
        self.assertEquals(submission.via, 'email')

    def test_2_submit_user(self):
        now = time.mktime(time.gmtime())
        msg = TESTEMAIL % { 'from': 'test@test.com',
            'to': 'hunt+emailtest@1hph.com',
            'subject': 'test 1',
            'date': formatdate(now) }
        environ = { 'RECIPIENT': 'hunt+emailtest@1hph.com', 'SENDER': 'paulw@test.com' }
        submission = email.submit_from_file(environ, StringIO(msg))
        self.assert_(submission)
        self.assertEquals(submission.user, self.user)
        self.assertEquals(submission.hunt, self.hunt)
        self.assert_(submission.photo)
        self.assertEquals(submission.photo_width, 240)
        self.assertEquals(submission.photo_height, 180)
        self.assertEquals(submission.anon_source, None)
        self.assertEquals(submission.via, 'email')

    def test_3_invalid_to(self):
        now = time.mktime(time.gmtime())
        msg = TESTEMAIL % { 'from': 'test@test.com',
            'to': 'foo',
            'subject': 'test 1',
            'date': formatdate(now) }
        environ = { 'SENDER': 'paulw@test.com' }
        self.assertRaises(email.InvalidAddress,
                          lambda: email.submit_from_file(environ, StringIO(msg)))

        environ = { 'RECIPIENT': 'hunt@1hph.com', 'SENDER': 'paulw@test.com' }
        self.assertRaises(email.InvalidAddress,
                          lambda: email.submit_from_file(environ, StringIO(msg)))

    def test_3_invalid_hunt(self):
        now = time.mktime(time.gmtime())
        msg = TESTEMAIL % { 'from': 'test@test.com',
            'to': 'foo',
            'subject': 'test 1',
            'date': formatdate(now) }
        environ = { 'RECIPIENT': 'hunt+@1hph.com', 'SENDER': 'paulw@test.com' }
        self.assertRaises(email.HuntDoesNotExist,
                          lambda: email.submit_from_file(environ, StringIO(msg)))

        environ = { 'RECIPIENT': 'hunt+foo@1hph.com', 'SENDER': 'paulw@test.com' }
        self.assertRaises(email.HuntDoesNotExist,
                          lambda: email.submit_from_file(environ, StringIO(msg)))

    def test_4_not_current(self):
        now = time.mktime((2009,5,20,1,2,3,0,0,0))
        msg = TESTEMAIL % { 'from': 'test@test.com',
            'to': 'foo',
            'subject': 'test 1',
            'date': formatdate(now) }
        environ = { 'RECIPIENT': 'hunt+emailtest@1hph.com', 'SENDER': 'paulw@test.com' }
        self.assertRaises(email.HuntNotCurrent,
                          lambda: email.submit_from_file(environ, StringIO(msg)))

        now = time.mktime((2020,5,20,1,2,3,0,0,0))
        msg = TESTEMAIL % { 'from': 'test@test.com',
            'to': 'foo',
            'subject': 'test 1',
            'date': formatdate(now) }
        environ = { 'RECIPIENT': 'hunt+emailtest@1hph.com', 'SENDER': 'paulw@test.com' }
        self.assertRaises(email.HuntNotCurrent,
                          lambda: email.submit_from_file(environ, StringIO(msg)))

    def test_5_not_multipart(self):
        self.assertRaises(email.NoImage,
                          lambda: email.submit_from_file({}, StringIO(NOT_MULTIPART)))

    def test_6_invalid_image(self):
        now = time.mktime(time.gmtime())
        msg = NOT_AN_IMAGE % { 'content_type': 'text/rtf' }
        environ = { 'RECIPIENT': 'hunt+emailtest@1hph.com', 'SENDER': 'paulw@test.com' }
        self.assertRaises(email.NoImage,
                          lambda: email.submit_from_file(environ, StringIO(msg)))

        msg = NOT_AN_IMAGE % { 'content_type': 'image/jpg' }
        environ = { 'RECIPIENT': 'hunt+emailtest@1hph.com', 'SENDER': 'paulw@test.com' }
        self.assertRaises(email.NoImage,
                          lambda: email.submit_from_file(environ, StringIO(msg)))


