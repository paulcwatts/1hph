from django import forms
from django.forms import widgets
from gonzo.hunt import models

class SubmissionForm(forms.ModelForm):
    class Meta:
        model = models.Submission
        fields = ['photo','latitude','longitude','source_via']
        widgets = {
            'latitude': widgets.HiddenInput(),
            'longitude': widgets.HiddenInput(),
            'source_via': widgets.HiddenInput(attrs={'value':'Web'})
        }
