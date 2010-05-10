from datetime import datetime
import pytz

from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin
from django.core.urlresolvers import reverse

from gonzo.utils import slugify
from gonzo.hunt import utils
from gonzo.hunt.thumbs import ImageWithThumbsField

def to_json_time(d):
    return d.replace(tzinfo=pytz.utc).isoformat()


class Hunt(models.Model):
    """
    The model for a hunt.

    start_time is inclusive, but end_time and vote_end_time are exclusive
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

    class State:
        FUTURE = "FUTURE"
        CURRENT = "CURRENT"
        VOTING = "VOTING"
        FINISHED = "FINISHED"

    def get_state(self):
        """
        Returns one of the following strings: FUTURE, CURRENT, VOTING, FINISHED
        For hunts where end_time == vote_end_time, there is no "VOTING" state.
        """
        now = datetime.utcnow()
        # Note start time is inclusive, but end time is exclusive.
        if now >= self.vote_end_time:
            return Hunt.State.FINISHED
        elif now >= self.end_time:
            return Hunt.State.VOTING
        elif now >= self.start_time:
            return Hunt.State.CURRENT
        else:
            return Hunt.State.FUTURE

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

    def get_thumbnail_url(self):
        try:
            return self.submission_set.filter(is_removed=False)[0].photo.url_240x180
        except IndexError:
            return None

    def to_dict(self,request):
        json = { 'owner': self.owner.username,
                'phrase': self.phrase,
                'slug': self.slug,
                'tag': self.tag,
                'start_time': to_json_time(self.start_time),
                'end_time': to_json_time(self.end_time),
                'vote_end_time': to_json_time(self.vote_end_time),
                'url': request.build_absolute_uri(self.get_absolute_url()),
                'submissions': request.build_absolute_uri(self.get_submission_url()),
                'ballot': request.build_absolute_uri(self.get_ballot_url()),
                'comments': request.build_absolute_uri(self.get_comments_url()) }
        thumb = self.get_thumbnail_url()
        if thumb:
            json['thumbnail'] = request.build_absolute_uri(thumb)
        return json

class Submission(models.Model):
    hunt            = models.ForeignKey(Hunt)
    time            = models.DateTimeField(default=datetime.utcnow)
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
    # TODO: To add when we get around to updating the model:
    #remove_reason = models.CharField(max_length=32)
    #description   = models.TextField()
    # for right now, we will generate 5 character paths.
    #shortened_path = models.CharField(unique=True,max_length=6,default=shorten_id)
    # The MD5 sum will be used to see if there are any duplicates in the hunt
    #md5sum        = models.CharField(max_length=32)

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

    def get_source(self):
        return utils.get_source(self)

    def to_dict(self,request):
        json = { 'time': to_json_time(self.time),
                'url': request.build_absolute_uri(self.get_absolute_url()),
                'photo_url': request.build_absolute_uri(self.photo.url),
                'thumbnail_url': request.build_absolute_uri(self.photo.url_240x180),
                'comments': request.build_absolute_uri(self.get_comments_url()) }
        if self.latitude:
            json['latitude'] = self.latitude
        if self.longitude:
            json['longitude'] = self.longitude
        json['source'] = utils.get_source_json(request, self)
        return json


class Comment(models.Model):
    hunt            = models.ForeignKey(Hunt)
    submission      = models.ForeignKey(Submission, null=True)
    time            = models.DateTimeField(default=datetime.utcnow)
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

    def get_source(self):
        return utils.get_source(self)

    def to_dict(self, request):
        return {
            'time': to_json_time(self.time),
            'source': utils.get_source_json(request, self),
            'text': self.text }

class Vote(models.Model):
    hunt            = models.ForeignKey(Hunt)
    submission      = models.ForeignKey(Submission)
    time            = models.DateTimeField(default=datetime.utcnow)
    value           = models.IntegerField()

    # Null means this comes from an unauthenticated user
    user            = models.ForeignKey(User,null=True)
    # For anonymous entries, this will keep track of from where we found it.
    # This takes a URL form like twitter:<username> or facebook:<profile_id>
    anon_source     = models.CharField(max_length=64,null=True,blank=True)
    ip_address      = models.IPAddressField(blank=True)

    # Make sure that, if there is a submission, and there is a hunt,
    # they are the same (a bit of a normalization problem)
    def clean(self):
        if self.hunt and self.submission:
            if self.hunt.id != self.submission.id:
                raise ValidationError("The submission isn't part of the same hunt")
        super(Award,self).clean()

    def __unicode__(self):
        return "%s %s %+d" % (self.hunt.slug, self.user or self.anon_source, self.value)

    def get_source(self):
        return utils.get_source(self)

#
# This class captures any awards given to each submission.
# For instance, "Hunt Winner" is the most common.
#
class Award(models.Model):
    GOLD = 1
    SILVER = 2
    BRONZE = 3

    AWARDS = (
        (GOLD,   'Gold Medal'),
        (SILVER, 'Silver Medal'),
        (BRONZE, 'Bronze Medal'),
    )

    hunt            = models.ForeignKey(Hunt)
    # If we want to have any hunt-wide awards, rather than one
    # tied to a permission
    submission      = models.ForeignKey(Submission,null=True,blank=True)
    # If submission=null, then this is the user awarded
    # If submission!=null, then this should be equal to submission.user
    user            = models.ForeignKey(User,null=True)
    anon_source     = models.CharField(max_length=64,null=True,blank=True)
    value           = models.IntegerField(choices=AWARDS)

    # Make sure that, if there is a submission, and there is a hunt,
    # they are the same (a bit of a normalization problem)
    def clean(self):
        if self.hunt and self.submission:
            if self.hunt.id != self.submission.id:
                raise ValidationError("The submission isn't part of the same hunt")
        super(Award,self).clean()

    def __unicode__(self):
        return '%s %s %s' % (self.hunt.slug, self.user or self.anon_source, self.value)

    def get_source(self):
        return utils.get_source(self)

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
