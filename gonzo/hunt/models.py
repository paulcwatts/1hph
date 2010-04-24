from datetime import datetime

from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin
from gonzo.utils import slugify

def json_encode(request):
    def wrap(obj):
        if 'json_encode' in obj.__class__.__dict__:
            return obj.json_encode(request)
        raise TypeError("Unable to encode: " + str(type(obj)))
    return wrap

class Hunt(models.Model):
    """
    The model for a hunt.
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
    vote_end_time    = models.DateTimeField()
    max_submissions  = models.PositiveIntegerField(null=True,blank=True)

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.start_time >= self.end_time:
            raise ValidationError("Start time must be earlier than end time")
        if self.end_time > self.vote_end_time:
            raise ValidationError("End time must be earlier (or equal to) end time")
        super(Hunt,self).clean()

    def __unicode__(self):
        return self.slug

    class Meta:
        ordering = ["-start_time"]

    def save(self, **kwargs):
        self.clean()
        self.slug = slugify(Hunt, self.phrase, exclude_pk=self.id)
        return super(Hunt,self).save(**kwargs)

    @models.permalink
    def get_absolute_url(self):
        return ('hunt', (), { 'slug' : self.slug })
    @models.permalink
    def get_api_url(self):
        return ('api-hunt', (), { 'slug' : self.slug })

    def json_encode(self,request):
        return { 'owner': self.owner.username,
                'phrase': self.phrase,
                'slug': self.slug,
                'tag': self.tag,
                'start_time': self.start_time.isoformat(),
                'end_time': self.end_time.isoformat(),
                'vote_end_time': self.vote_end_time.isoformat(),
                'url': request.build_absolute_uri(self.get_absolute_url()) }

class Submission(models.Model):
    hunt            = models.ForeignKey(Hunt)
    time            = models.DateTimeField(default=datetime.now())
    # The URL to the photo
    photo           = models.ImageField(upload_to="photos", max_length=256)
    # The URL to the thumbnail
    thumbnail       = models.ImageField(upload_to="photos", null=True, max_length=256)
    # The Source URL (person)
    source          = models.URLField()
    # How the source was submitted (Twitter, Facebook, 1hph for Android)
    source_via      = models.CharField(max_length=64)
    # Location of submission
    latitude        = models.FloatField(null=True,blank=True)
    longitude       = models.FloatField(null=True,blank=True)

    class Meta:
        ordering = ["-time"]

    def __unicode__(self):
        return "%s:%s" % (self.hunt.slug, self.source)

    @models.permalink
    def get_absolute_url(self):
        return ('photo', (), { 'slug' : self.hunt.slug, 'photo_id' : self.id })
    @models.permalink
    def get_api_url(self):
        return ('api-photo', (), { 'slug' : self.hunt.slug, 'photo_id' : self.id })

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
