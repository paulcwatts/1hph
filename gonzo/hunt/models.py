from datetime import datetime

from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin

def json_encode(request):
    def wrap(obj):
        if 'json_encode' in obj.__class__.__dict__:
            return obj.json_encode(request)
        raise TypeError("Unable to encode: " + str(type(obj)))
    return wrap

class Hunt(models.Model):
    """
    A model for a hunt

    >>> from gonzo.hunt.models import Hunt
    """
    # Owner of the hunt
    owner            = models.ForeignKey(User)
    # Three word phrase (crazy model submarine)
    phrase           = models.CharField(max_length=128)
    # The hunt slug (based on the phrase)
    slug             = models.SlugField(unique=True,max_length=200)
    # The hunt tag (to be used as hashtag)
    tag              = models.CharField(max_length=64)
    start_time       = models.DateTimeField()
    end_time         = models.DateTimeField()
    max_submissions  = models.PositiveIntegerField(null=True,blank=True)
    # TODO: Invite list

    class Meta:
        ordering = ["-start_time"]

    @models.permalink
    def get_absolute_url(self):
        return ('hunt', (), { 'slug' : self.slug })
    def json_encode(self,request):
        return { 'owner': self.owner.username,
                'phrase': self.phrase,
                'slug': self.slug,
                'tag': self.tag,
                'start_time': self.start_time.isoformat(),
                'end_time': self.end_time.isoformat(),
                'url': request.build_absolute_uri(self.get_absolute_url()) }

class Submission(models.Model):
    hunt            = models.ForeignKey(Hunt)
    time            = models.DateTimeField(default=datetime.now())
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

#
# This class captures any awards given to each submission.
# For instance, "Hunt Winner" is the most common.
#
class Award(models.Model):
    hunt            = models.ForeignKey(Hunt)
    submission      = models.ForeignKey(Submission)
    value           = models.IntegerField()

#
# Admin
#
class HuntAdmin(admin.ModelAdmin):
    list_display = ('slug','start_time')
    prepopulated_fields = {"slug":("phrase",)}

admin.site.register(Hunt, HuntAdmin)
admin.site.register(Submission)
admin.site.register(Comment)
admin.site.register(Vote)
admin.site.register(Award)
