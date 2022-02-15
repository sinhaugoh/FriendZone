from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import login, authenticate

from .forms import RegistrationForm

# Create your views here.
def index(request):
    user = request.user
    
    if user.is_authenticated:
        return render(request, 'social_media/index.html')
    else:
        # TODO: change the redirect to login
        return redirect('register')

def register(request):
    user = request.user
    
    if user.is_authenticated:
        return HttpResponse('Already Authenticated!')
    
    if request.method == 'POST':
        # form submission
        registration_form = RegistrationForm(data=request.POST)
        
        if registration_form.is_valid():
            new_user = registration_form.save()
            new_user.set_password(new_user.password)
            new_user.save()
            
            # login the new user
            login(request, new_user)
            
            # redirect to home page if registration successful
            return redirect('index')
            
    else:
        # form retrieval
        registration_form = RegistrationForm()
    

    return render(request, 'social_media/user_registration.html', {
        'registration_form': registration_form
        })