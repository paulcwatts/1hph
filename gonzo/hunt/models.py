from django.db import models
import pycassa

print 'connecting'
CLIENT = pycassa.connect_thread_local(framed_transport=True)
KEYSPACE = 'Gonzo'

HUNTS       = pycassa.ColumnFamily(CLIENT, KEYSPACE, 'Hunts')
#SUBMISSIONS = pycassa.ColumnFamily(CLIENT, KEYSPACE, 'Submissions')
#VOTES       = pycassa.ColumnFamily(CLIENT, KEYSPACE, 'Votes')
#COMMENTS    = pycassa.ColumnFamily(CLIENT, KEYSPACE, 'Comments')
# TODO: Achievements???

#
# Requirements of a hunt:
# It should be ordered by time
# It can appear as a URL
# http://1hph.com/hunt/crazy-fool-plant
#

class Hunt(object):
    """
    A cassandra model for a Hunt

    >>> h = Hunt()
    >>> h.key = 'myhunt'
    >>> h.phrase = 'sexy chocolate camper'
    >>> h.slug = 'sexy-chocolate'
    >>> from datetime import datetime
    >>> h.start_time = datetime.now()
    >>> h.end_time = h.start_time + 1000
    >>> ts = Hunt.objects.insert(h)
    """
    key             = pycassa.String()
    owner           = pycassa.String()
    # The hunt phrase (scary awkward clown)
    phrase          = pycassa.String()
    # The hunt phrase that can be used as part of a URL or hashtag
    slug            = pycassa.String()
    # The start time of the hunt
    start_time      = pycassa.DateTimeString()
    # The end time of the hunt
    end_time        = pycassa.DateTimeString()
    # The maximum number of submissions for this hunt. None = no limit.
    max_submissions = pycassa.IntString()

Hunt.objects = pycassa.ColumnFamilyMap(Hunt, HUNTS)


