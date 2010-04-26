from datetime import datetime

from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin
from gonzo.utils import slugify
from gonzo.hunt.utils import get_source_json
from gonzo.hunt.thumbs import ImageWithThumbsField

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

    def _get_url(self,viewname):
        return (viewname, (), { 'slug' : self.slug })

    @models.permalink
    def get_absolute_url(self):
        return self._get_url('hunt')
    @models.permalink
    def get_api_url(self):
        return self._get_url('api-hunt')
    @models.permalink
    def get_submission_url(self):
        return self._get_url('api-photo-index')

    def to_dict(self,request):
        return { 'owner': self.owner.username,
                'phrase': self.phrase,
                'slug': self.slug,
                'tag': self.tag,
                'start_time': self.start_time.isoformat(),
                'end_time': self.end_time.isoformat(),
                'vote_end_time': self.vote_end_time.isoformat(),
                'url': request.build_absolute_uri(self.get_absolute_url()),
                'submissions': request.build_absolute_uri(self.get_submission_url()) }

class Submission(models.Model):
    hunt            = models.ForeignKey(Hunt)
    time            = models.DateTimeField(default=datetime.now())
    # The URL to the photo
    photo           = ImageWithThumbsField(upload_to="photos",
                                        max_length=256,
                                        height_field='photo_height',
                                        width_field='photo_width',
                                        sizes=((240,180),))
    photo_width     = models.IntegerField()
    photo_height    = models.IntegerField()

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

    def _get_url(self,viewname):
        return (viewname, (), { 'slug' : self.hunt.slug, 'object_id' : self.id })

    @models.permalink
    def get_absolute_url(self):
        return self._get_url('photo')
    @models.permalink
    def get_api_url(self):
        return self._get_url('api-photo')
    @models.permalink
    def get_comments_url(self):
        return self._get_url('api-photo-comments')
    @models.permalink
    def get_comment_stream_url(self):
        return self._get_url('api-photo-comment-stream')

    def to_dict(self,request):
        json = { 'time': self.time.isoformat(),
                'url': request.build_absolute_uri(self.get_absolute_url()),
                'photo_url': request.build_absolute_uri(self.photo.url),
                'thumbnail_url': request.build_absolute_uri(self.photo.url_240x180),
                'comments': request.build_absolute_uri(self.get_comments_url()) }
        if self.latitude:
            json['latitude'] = self.latitude
        if self.longitude:
            json['longitude'] = self.longitude
        json['source'] = get_source_json(request, self.source, self.source_via)
        return json


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
