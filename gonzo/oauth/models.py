import random
from datetime import datetime
from urlparse import urlparse

from django.db import models
from django.contrib.auth.models import User

# Note that default value of allowed_chars does not have "I" or letters
# that look like it -- just to avoid confusion.
KEYSPACE="abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789"
KEYSIZE=32

def random_string(length):
    return ''.join([random.choice(KEYSPACE) for i in range(length)])

def generate_key():
    return random_string(KEYSIZE)

class Consumer(models.Model):
    """
    A consumer is the 'client' in OAuth new parlance.
    It is a particular application that wishes to access resources.
    """
    key = models.CharField(max_length=KEYSIZE,unique=True,default=generate_key)
    secret = models.CharField(max_length=KEYSIZE,default=generate_key)
    is_revoked = models.BooleanField(default=False,blank=True)

    # This is user metadata regarding the particular application
    name = models.CharField(max_length=64,unique=True)
    # The URL to the application
    url = models.URLField()

class RequestToken(models.Model):
    """
    This can either represent a request token or an access token.
    """
    key = models.CharField(max_length=KEYSIZE,primary_key=True,default=generate_key)
    secret = models.CharField(max_length=KEYSIZE)
    consumer = models.ForeignKey(Consumer)
    callback = models.URLField()

class AccessToken(models.Model):
    key = models.CharField(max_length=KEYSIZE,primary_key=True,default=generate_key)
    secret = models.CharField(max_length=KEYSIZE)
    consumer = models.ForeignKey(Consumer)
    # This is the user that has been granted access
    user = models.ForeignKey(User,null=True)
    # Access tokens may not have expire times or refresh tokens
    expiry_time = models.DateTimeField(null=True)
    refresh_token = models.CharField(max_length=KEYSIZE,null=True)
    # TODO: Secret type and secret hash

class VerificationKey(models.Model):
    """
    This is the verifier that is passed back after the user has authorized the consumer.
    We keep track of it because it gets expired after a certain short period of time.
    """
    consumer = models.ForeignKey(Consumer)
    redirection_uri = models.URLField()
    code = models.CharField(max_length=32)
    expiry_time = models.DateTimeField()
    # Used or expired verification keys will be purged at some point.
    confirmed = models.BooleanField(default=False,blank=True)

    def clean(self):
        from django.core.exceptions import ValidationError
        url = urlparse(self.redirection_uri)
        if not url.scheme or not url.hostname:
            raise ValidationError("Redirection URL must have scheme (HTTP or HTTPS) and hostname")
        super(Hunt,self).clean()


class RequestLog(models.Model):
    """
    Prevents replay attacks.

    These are cleaned out fairly frequently, as any timestamp off by 5 minutes will be denied.
    """
    consumer = models.ForeignKey(Consumer)
    nonce = models.CharField(max_length=100)
    timestamp = models.DateTimeField()

    class Meta:
        unique_together = ('consumer','nonce',)
