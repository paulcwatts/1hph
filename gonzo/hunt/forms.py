from django import forms
from django.forms import widgets
from gonzo.hunt import models

class SubmissionForm(forms.ModelForm):
    class Meta:
        model = models.Submission
        fields = ['photo','latitude','longitude','via']
        widgets = {
            'latitude': widgets.HiddenInput(),
            'longitude': widgets.HiddenInput(),
            'via': widgets.HiddenInput(attrs={'value':'Web'})
        }
    valid_check = forms.BooleanField()

class CommentForm(forms.ModelForm):
    class Meta:
        model = models.Comment
        fields = ['text']
