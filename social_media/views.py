from django.urls import reverse
from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
from django.contrib.auth import login, authenticate, logout
from django.views.decorators.cache import never_cache

from .models import AppUser

from .forms import RegistrationForm, LoginForm

# Create your views here.
def index(request):
    user = request.user
    
    if user.is_authenticated:
        # authenticated
        return render(request, 'social_media/index.html')
    else:
        # not authenticated
        return redirect('login')
    
@never_cache
def user_login(request, *args, **kwargs):
    user = request.user
    
    if user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':
        login_form = LoginForm(data=request.POST)
        
        # if form is valid
        if login_form.is_valid():
            email = login_form.cleaned_data['email']
            password = login_form.cleaned_data['password']
            
            user = authenticate(email=email, password=password)
            
            if user:
                # if authenticated
                login(request, user)
                
                # navigate to home page
                return redirect('index')
    else:
        login_form = LoginForm()
        
    return render(request, 'social_media/login.html', {'login_form': login_form})

def register(request):
    user = request.user
    
    if user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':
        # form submission
        registration_form = RegistrationForm(data=request.POST)
        
        if registration_form.is_valid():
            new_user = registration_form.save()
            
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
    
def user_logout(request):
    logout(request)
    
    return redirect('index')

def profile(request, id):
    user = request.user
    
    if user.is_authenticated:
        # authenticated
        # get the requested user
        requested_user = None
        try:
            requested_user = AppUser.objects.get(id=id)
        except AppUser.DoesNotExist:
            # requested user does not exist
            raise Http404('This page is not available')
        
        context = {}
            
        if request.method == 'POST':
            pass
        else:
            context['username'] = requested_user.username
            context['email'] = requested_user.email
            context['profile_image_url'] = requested_user.profile_image.url

            if user.id == requested_user.id:
                # if the user accessing own profile
                context['is_own_profile'] = True
            else:
                # if the user accessing other profile
                context['is_own_profile'] = False
    else:
        # not authenticated
        # TODO: can be changed so that people that are not authenticated can view certain info
        return redirect('login')
        
    return render(request, 'social_media/profile.html', context)