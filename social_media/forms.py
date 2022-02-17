from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm

from .models import AppUser

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(max_length=256, required=True)
    
    class Meta:
        model = AppUser
        fields = ('email', 'username', 'password1', 'password2')
        
    def clean_email(self):
        # convert input email to lowercase
        email = self.cleaned_data['email'].lower()
        
        try:
            # try to retrieve a database instance with the same input
            # if exist, raise error, else return lower case version of the input
            AppUser.objects.get(email=email)
            raise forms.ValidationError('Email is already in use.')
        except AppUser.DoesNotExist:
            return email
        
    def clean_username(self):
        # convert input username to lowercase
        username = self.cleaned_data['username'].lower()
        
        try:
            # try to retrieve a database instance with the same input
            # if exist, raise error, else return lower case version of the input
            AppUser.objects.get(username=username)
            raise forms.ValidationError('Username already in use.')
        except AppUser.DoesNotExist:
            return username
        
class LoginForm(forms.ModelForm):
    # make password a password input
    password = forms.CharField(label='Password', required=True, widget=forms.PasswordInput)

    class Meta:
        model = AppUser
        fields = ('email', 'password')

    def clean_email(self):
        # convert input email into lowercase
        return self.cleaned_data['email'].lower()

    def clean(self):
        if self.is_valid():
            email = self.cleaned_data['email']
            password = self.cleaned_data['password']
            user = authenticate(email=email, password=password)

            if not user:
                # if user does not exist
                raise forms.ValidationError("Incorrect email or password. Please try again")
            
        return self.cleaned_data
    
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = AppUser
        fields = ('profile_image', 'email', 'username')
        
    def clean_email(self):
        # convert input email to lowercase
        email = self.cleaned_data['email'].lower()
        
        try:
            # try to retrieve a database instance with the same input
            # if exist, raise error, else return lower case version of the input
            AppUser.objects.exclude(pk=self.instance.pk).get(email=email)
            raise forms.ValidationError('Email is already in use.')
        except AppUser.DoesNotExist:
            return email
        
    def clean_username(self):
        # convert input username to lowercase
        username = self.cleaned_data['username'].lower()
        
        try:
            # try to retrieve a database instance with the same input
            # if exist, raise error, else return lower case version of the input
            AppUser.objects.exclude(pk=self.instance.pk).get(username=username)
            raise forms.ValidationError('Username already in use.')
        except AppUser.DoesNotExist:
            return username
        
    # def save(self, commit=True):
    #     app_user = super(ProfileUpdateForm, self).save(commit=False)
    #     print(self.cleaned_data['profile_image'])
    #     app_user.profile_image = self.cleaned_data['profile_image']
    #     if commit:
    #         app_user.save()
            
    #     return app_user