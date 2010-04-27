from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class UserCreationFormWithEmail(UserCreationForm):
    email = forms.EmailField()

    def clean_email(self):
        # Superusers can create as many accounts as they want
        # through the admin interface.
        # otherwise we restrict it to one account per email
        email = self.cleaned_data["email"]
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
