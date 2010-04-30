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

    def clean_valid_check(self):
        check = self.cleaned_data["valid_check"]
        if not check:
            raise forms.ValidationError("Please check the box.")
        return True

class CommentForm(forms.ModelForm):
    class Meta:
        model = models.Comment
        fields = ['text']
