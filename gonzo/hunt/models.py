from django.db import models


class Hunt(models.Model):
    """
    A model for a hunt

    >>> from gonzo.hunt.models import Hunt
    """
    # Owner of the hunt
    owner            = models.URLField(null=True)
    # Three word phrase (crazy model submarine)
    phrase           = models.CharField(max_length=128)
    # The hunt slug (based on the phrase)
    slug             = models.SlugField(unique=True,max_length=200)
    # The hunt tag (to be used as hashtag)
    tag              = models.CharField(max_length=64)
    start_time       = models.DateTimeField()
    end_time         = models.DateTimeField()
    max_submissions  = models.PositiveIntegerField(null=True)

    # TODO: get_absolule_uri
    #@models.permalink
    #def get_absolute_url(self):
        #return ('hunt-permalink', (), { 'object_id' : self.slug })

# TODO: Write storage object for Rackspace Cloud Files
class Submission(models.Model):
    hunt            = models.ForeignKey(Hunt)
    time            = models.DateTimeField()
    # The URL to the photo
    photo           = models.ImageField(upload_to="submit/%Y/%m/%d", max_length=256)
    # The URL to the thumbnail
    thumbnail       = models.ImageField(upload_to="submit/%Y/%m/%d", null=True, max_length=256)
    # The Source URL (person)
    source          = models.URLField()
    # How the source was submitted (Twitter, Facebook, 1hph for Android)
    source_via      = models.CharField(max_length=64)
    # Location of submission
    latitude        = models.FloatField(null=True)
    longitude       = models.FloatField(null=True)
    # TODO: get_absolute_uri

class Comment(models.Model):
    hunt            = models.ForeignKey(Hunt)
    # This can be NULL in case we allow comments on a hunt in general
    submission      = models.ForeignKey(Submission, null=True)
    time            = models.DateTimeField()
    source          = models.URLField()
    text            = models.CharField(max_length=256)
    # TODO: get_absolute_uri

class Vote(models.Model):
    hunt            = models.ForeignKey(Hunt)
    submission      = models.ForeignKey(Submission)
    time            = models.DateTimeField()
    source          = models.URLField()
    value           = models.IntegerField()
