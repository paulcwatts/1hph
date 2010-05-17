from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from gonzo import settings
from gonzo.account.models import Profile

class UserCreationFormWithEmail(UserCreationForm):
    error_css_class = 'error'
    required_css_class = 'required'

    email = forms.EmailField()

    def clean_email(self):
        # Superusers can create as many accounts as they want
        # through the admin interface.
        # otherwise we restrict it to one account per email
        email = self.cleaned_data["email"]
        # First off, check the email whitelist
        if (len(settings.SIGNUP_EMAIL_WHITELIST) > 0 and
            email not in settings.SIGNUP_EMAIL_WHITELIST):
            raise forms.ValidationError("This email is not valid for signup right now.")

        users = User.objects.filter(email__iexact=email)
        if len(users) == 0:
            return email
        raise forms.ValidationError("That email is already in use by another account. Please choose another.")

    def save(self,commit=True):
        user = super(UserCreationFormWithEmail,self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class UserUpdateForm(forms.Form):
    error_css_class = 'error'
    required_css_class = 'required'
    """
    Allows the user to set his "User" data and some profile data in the same go.
    """
    first_name = forms.CharField(required=False,max_length=30)
    last_name = forms.CharField(required=False,max_length=30)
    email = forms.EmailField()
    user_location = forms.CharField(max_length=Profile.LOCATION_MAX_LEN,
                                    required=False,
                                    label='Your location',
                                    help_text='Where are you?')


class PhotoUpdateForm(forms.Form):
    error_css_class = 'error'
    required_css_class = 'required'
    photo = forms.ImageField()

