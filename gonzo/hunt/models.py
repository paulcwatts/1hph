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
    def get_ballot_url(self):
        return self._get_url('api-hunt-ballot')
    @models.permalink
    def get_submission_url(self):
        return self._get_url('api-photo-index')
    @models.permalink
    def get_comments_url(self):
        return self._get_url('api-hunt-comment-index')

    def to_dict(self,request):
        return { 'owner': self.owner.username,
                'phrase': self.phrase,
                'slug': self.slug,
                'tag': self.tag,
                'start_time': self.start_time.isoformat(),
                'end_time': self.end_time.isoformat(),
                'vote_end_time': self.vote_end_time.isoformat(),
                'url': request.build_absolute_uri(self.get_absolute_url()),
                'submissions': request.build_absolute_uri(self.get_submission_url()),
                'ballot': request.build_absolute_uri(self.get_ballot_url()),
                'comments': request.build_absolute_uri(self.get_comments_url()) }

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

    # Location of submission
    latitude        = models.FloatField(null=True,blank=True)
    longitude       = models.FloatField(null=True,blank=True)

    # Null means this comes from an unauthenticated user
    user            = models.ForeignKey(User,null=True)
    # For anonymous entries, this will keep track of from where we found it.
    # This takes a URL form like twitter:<username> or facebook:<profile_id>
    anon_source     = models.CharField(max_length=64,null=True,blank=True)
    ip_address      = models.IPAddressField(blank=True)
    # Where this was submitted, e.g., "Web" "Twitter", "1hph for Android"
    via             = models.CharField(max_length=32)
    is_removed      = models.BooleanField(default=False)

    class Meta:
        ordering = ["-time"]

    def __unicode__(self):
        return "%s %s" % (self.hunt.slug, self.user or self.anon_source)

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
        return self._get_url('api-photo-comment-index')
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
        json['source'] = get_source_json(request, self)
        return json


class Comment(models.Model):
    hunt            = models.ForeignKey(Hunt)
    submission      = models.ForeignKey(Submission, null=True)
    time            = models.DateTimeField(default=datetime.now())
    text            = models.CharField(max_length=256)

    # Null means this comes from an unauthenticated user
    user            = models.ForeignKey(User,null=True)
    # For anonymous entries, this will keep track of from where we found it.
    # This takes a URL form like twitter:<username> or facebook:<profile_id>
    anon_source     = models.CharField(max_length=64,null=True,blank=True)
    ip_address      = models.IPAddressField(blank=True)
    is_removed      = models.BooleanField(default=False)

    class Meta:
        ordering = ["-time"]

    def __unicode__(self):
        return u"%s %s %s" % (self.hunt.slug, self.user or self.anon_source, self.text)

    @models.permalink
    def get_api_url(self):
        if self.submission:
            return ('api-photo-comment', (),
                    { 'slug': self.hunt.slug,
                      'object_id': self.submission.id,
                      'comment_id': self.id })
        else:
            return ('api-hunt-comment', (),
                    { 'slug': self.hunt.slug,
                      'comment_id': self.id })

    def to_dict(self, request):
        return {
            'time': self.time.isoformat(),
            'source': get_source_json(request, self),
            'text': self.text }

class Vote(models.Model):
    hunt            = models.ForeignKey(Hunt)
    submission      = models.ForeignKey(Submission)
    time            = models.DateTimeField(default=datetime.now())
    value           = models.IntegerField()

    # Null means this comes from an unauthenticated user
    user            = models.ForeignKey(User,null=True)
    # For anonymous entries, this will keep track of from where we found it.
    # This takes a URL form like twitter:<username> or facebook:<profile_id>
    anon_source     = models.CharField(max_length=64,null=True,blank=True)
    ip_address      = models.IPAddressField(blank=True)

    def __unicode__(self):
        return "%s %s %+d" % (self.hunt.slug, self.user or self.anon_source, self.value)

#
# This class captures any awards given to each submission.
# For instance, "Hunt Winner" is the most common.
#
class Award(models.Model):
    AWARDS = (
        (1, 'Gold Medal'),
        (2, 'Silver Medal'),
        (3, 'Bronze Medal'),
    )

    hunt            = models.ForeignKey(Hunt)
    # If we want to have any hunt-wide awards, rather than one
    # tied to a permission
    submission      = models.ForeignKey(Submission,null=True)
    # If submission=null, then this is the user awarded
    # If submission!=null, then this should be equal to submission.user
    user            = models.ForeignKey(User,null=True)
    anon_source     = models.CharField(max_length=64,null=True,blank=True)
    value           = models.IntegerField(choices=AWARDS)

    def __unicode__(self):
        return '%s %s %s' % (self.hunt.slug, self.user or self.anon_source, self.value)

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
