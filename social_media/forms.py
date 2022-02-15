from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import AppUser

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(max_length=256, required=True)
    
    class Meta:
        model = AppUser
        fields = ('email', 'username', 'password1', 'password2')
        
    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        
        try:
            # try to retrieve a database instance with the same input
            # if exist, raise error, else return lower case version of the input
            AppUser.objects.get(email=email)
            raise forms.ValidationError('Email is already in use.')
        except AppUser.DoesNotExist:
            return email
        
    def clean_username(self):
        username = self.cleaned_data['username'].lower()
        
        try:
            # try to retrieve a database instance with the same input
            # if exist, raise error, else return lower case version of the input
            AppUser.objects.get(username=username)
            raise forms.ValidationError('Username already in use.')
        except AppUser.DoesNotExist:
            return username
        
        