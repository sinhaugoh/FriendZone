from django.shortcuts import render, redirect
from django.http import Http404, HttpResponse
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.views.decorators.cache import never_cache
from django.db.models import Q
from django.contrib.auth.forms import PasswordChangeForm

from .models import DEFAULT_PROFILE_IMAGE_PATH, AppUser

from .forms import RegistrationForm, LoginForm, ProfileUpdateForm

# Create your views here.


def index(request):
    app_user = request.user

    if app_user.is_authenticated:
        # authenticated
        return render(request, 'social_media/index.html')
    else:
        # not authenticated
        return redirect('login')


@never_cache
def user_login(request):
    app_user = request.user

    if app_user.is_authenticated:
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
    app_user = request.user

    if app_user.is_authenticated:
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
    
def password_change(request):
    app_user = request.user

    if app_user.is_authenticated:
        if request.method == 'POST':
            password_change_form = PasswordChangeForm(data=request.POST, user=app_user)   
            
            if password_change_form.is_valid():
                password_change_form.save()
                update_session_auth_hash(request, password_change_form.user)
                
                return redirect('index')
        else:
            password_change_form = PasswordChangeForm(user=app_user)   
            
        return render(request, 'social_media/change_password.html', {'password_change_form': password_change_form})
    else:
        # not authenticated
        return redirect('login')


def user_logout(request):
    logout(request)

    return redirect('index')


def profile(request, id):
    app_user = request.user

    if app_user.is_authenticated:
        # authenticated
        # get the requested user
        requested_user = None
        try:
            requested_user = AppUser.objects.get(pk=id)
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

            if app_user.id == requested_user.id:
                # if the user accessing own profile
                context['is_own_profile'] = True
            else:
                # if the user accessing other profile
                context['is_own_profile'] = False

        return render(request, 'social_media/profile.html', context)
    else:
        # not authenticated
        # TODO: can be changed so that people that are not authenticated can view certain info
        return redirect('login')


def search_user(request):
    app_user = request.user

    if app_user.is_authenticated:
        if request.method == 'GET':
            search_input = request.GET.get('query')
            context = {}

            if search_input:
                # if there is input
                results = []
                # get users where email or username contain the input
                user_results = AppUser.objects.filter(
                    Q(email__icontains=search_input) | Q(username__icontains=search_input))

                for user in user_results:
                    # user id, username, is_friend, is_own
                    results.append(
                        (user.id, user.username, False, user.id == app_user.id))

                context['user_results'] = results

        return render(request, 'social_media/search_result.html', context)
    else:
        # TODO: can be changed so that people that are not authenticated can view certain info
        return redirect('login')


def profile_update(request):
    app_user = request.user

    if app_user.is_authenticated:
        # authenticated
        try:
            user = AppUser.objects.get(pk=app_user.pk)
        except AppUser.DoesNotExist:
            return HttpResponse('Something gone wrong. Please try again.')
        
        if request.method == 'POST':
            profile_update_form = ProfileUpdateForm(
                request.POST, request.FILES, instance=user)

            if profile_update_form.is_valid():
                # # remove old profile image
                # old_image_path = user.profile_image.path
                # if os.path.exists(old_image_path):
                #     os.remove(old_image_path)

                profile_update_form.save()

                return redirect('profile', id=app_user.id)
        else:
            profile_update_form = ProfileUpdateForm(request.POST or None, instance=user)

        return render(request, 'social_media/update_profile.html', {'profile_update_form': profile_update_form})
    else:
        # not authenticated
        return redirect('login')
