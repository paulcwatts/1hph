from django import forms

from gonzo.connectors.twitter.models import TwitterProfile

class TwitterUpdateForm(forms.Form):
    notify_on_submit = forms.BooleanField(required=False,  label='I upload a photo')
    notify_on_award = forms.BooleanField(required=False,   label='I win an award')
    notify_on_comment = forms.BooleanField(required=False, label='I comment on a photo')
    notify_on_rank = forms.BooleanField(required=False,    label='I go up in rank')
    notify_on_vote = forms.BooleanField(required=False,    label='I vote in a hunt')

def get_form_for_user(user):
    try:
        profile = TwitterProfile.objects.get(user=user)
        return TwitterUpdateForm({
            'notify_on_submit': profile.notify_on_submit,
            'notify_on_award': profile.notify_on_award,
            'notify_on_comment': profile.notify_on_comment,
            'notify_on_rank': profile.notify_on_rank,
            'notify_on_vote': profile.notify_on_vote,
        })
    except TwitterProfile.DoesNotExist:
        # Return an unbound form.
        return TwitterUpdateForm()
