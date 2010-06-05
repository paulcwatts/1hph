from datetime import datetime

from django.db import transaction, connection
from django.db.models import Sum

from gonzo import settings
from gonzo.utils.middleware.debug import reformat_sql
from gonzo.hunt.models import *

@transaction.commit_on_success
def assign_awards():
    # First, get all hunts that have passed and have no awards assigned.
    # What we need is:
    # SELECT * FROM hunt_hunt h WHERE h.vote_end_time >= now AND
    #        h.id NOT IN (SELECT DISTINCT a.hunt_id from hunt_award a)
    now = datetime.utcnow()
    done = Award.objects.values_list('hunt_id', flat=True).distinct()
    entries = Hunt.objects.filter(vote_end_time__lte=now).exclude(pk__in=done).select_related()
    # entries is all the hunts that have not been assigned awards.
    # For each of them, get the sum of the votes for all the submissions,
    # and order them descending
    for h in entries:
        votes = []
        # There's probably a better way of doing this (all in SQL),
        # but who knows if it's fast at all.
        for s in h.submission_set.filter(is_removed=False):
            agg = s.vote_set.aggregate(Sum('value'))
            votes.append((s, agg['value__sum'] or 0))

        votes.sort(lambda lhs, rhs: rhs[1] - lhs[1])
        if len(votes) == 0:
            # No votes are assigned
            continue

        #
        # Awards are assigned:
        # If all votes are 0, then no awards are assigned
        # (this should only happen if len(votes) == 0
        #
        # We assign the highest votes the gold,
        # The second highest votes the silver,
        # And the third highest votes the bronze.
        # Ties share awards, but if there are more awards
        # given than 3 then there may not be silver or bronze.
        #
        current_vote_total = votes[0][1]
        awards = (Award.GOLD, Award.SILVER, Award.BRONZE)
        current_award = 0
        num_awards = 0

        for v in votes:
            submission = v[0]
            num = v[1]
            # At any point we reach entries with 0 votes, we stop
            if num == 0:
                break
            if num == current_vote_total:
                # Assign it the current award
                Award.objects.create(hunt=h,
                                 submission=submission,
                                 user=submission.user,
                                 anon_source=submission.anon_source,
                                 value=awards[current_award])
                num_awards += 1
            elif num_awards >= 3:
                # We've assigned enough
                break
            else:
                current_award += 1
                if current_award >= len(awards):
                    # No more awards
                    break
                current_vote_total = num
                Award.objects.create(hunt=h,
                                 submission=submission,
                                 user=submission.user,
                                 anon_source=submission.anon_source,
                                 value=awards[current_award])
                num_awards += 1

def delete_unplayed():
    """Removes any unplayed hunts."""
    # What we want is:
    # DELETE FROM hunt h where (h.vote_end_time <= now) AND
    #        (SELECT COUNT(*) from vote v where v.hunt_id == h.id) == 0
    hunts = Hunt.objects.filter(vote_end_time__lte=datetime.utcnow())
    for h in hunts:
        if h.vote_set.count() == 0:
            h.delete()

