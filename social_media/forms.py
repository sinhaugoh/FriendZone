from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

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

    # email = forms.EmailField(max_length=256, required=True)     
    
    # class Meta:
    #     model = AppUser
    #     fields = ('email', 'password')
        
    # def clean_email(self):
    #     # convert input email to lowercase
    #     email = self.cleaned_data['email'].lower()
    
    #     try:
    #         # try to retrieve a database instance with the same input
    #         # if exist, raise error, else return lower case version of the input
    #         AppUser.objects.get(email=email)
    #         raise forms.ValidationError('Email is already in use.')
    #     except AppUser.DoesNotExist:
    #         return email
    # def clean(self):
    #     # get email and password
    #     email = self.cleaned_data.get('email')
    #     password = self.cleaned_data.get('password')
        
    #     if email and password:
    #         self.user_cache = authenticate(email=email, password=password)
    #         if self.user_cache is None:
    #             # if email or password is not valid
    #             raise forms.ValidationError('Incorrect email of password. Please try again.')
    #         elif not self.user_cache.is_active:
    #             raise forms.ValidationError('This account is inactive')
        
    #     # check if cookie is enabled in the web browser
    #     self.check_for_test_cookie()
        
    #     return self.cleaned_data