from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect
from django.http import Http404
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.views.decorators.cache import never_cache
from django.db.models import Q
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required

from .models import AppUser, UserRelationship, Post
from .forms import RegistrationForm, LoginForm, ProfileUpdateForm

@login_required(login_url='/login/')
def index(request):
    '''
    Home page
    '''
    app_user = request.user

    # get all friends relationships with the app_user
    relationships = UserRelationship.objects.filter(
        Q(user1=app_user) | Q(user2=app_user), relation_type='friends')

    # a list of users where their post will be displayed
    post_users = [app_user]
    for relationship in relationships:
        if relationship.user1.pk == app_user.pk:
            post_users.append(relationship.user2)
        else:
            post_users.append(relationship.user1)

    # retrieve a list of posts
    posts = Post.objects.filter(owner__in=post_users).order_by('-date_created')
    post_list = []
    for post in posts:
        post_list.append({
            'owner_username': post.owner.username,
            'owner_profile_image_path': post.owner.profile_image.url,
            'post_text': post.text,
            'post_image_path': None if post.image == '' else post.image.url,
            'post_date_created': post.date_created
        })

    return render(request, 'social_media/index.html', {'posts': post_list})


@never_cache
def user_login(request):
    '''
    Login page
    '''
    app_user = request.user

    # redirect user to home page if already authenticated
    if app_user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        login_form = LoginForm(data=request.POST)

        # if input is valid
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
    '''
    Registration page
    '''
    app_user = request.user

    # redirect user to home page if already authenticated
    if app_user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        registration_form = RegistrationForm(data=request.POST)

        # if input is valid
        if registration_form.is_valid():
            new_user = registration_form.save()

            # login the new user
            login(request, new_user)

            # redirect to home page
            return redirect('index')

    else:
        # form retrieval
        registration_form = RegistrationForm()

    return render(request, 'social_media/user_registration.html', {
        'registration_form': registration_form
    })


@login_required(login_url='/login/')
def password_change(request):
    '''
    Change password page
    '''
    app_user = request.user

    if request.method == 'POST':
        password_change_form = PasswordChangeForm(
            data=request.POST, user=app_user)

        if password_change_form.is_valid():
            password_change_form.save()
            # this can prevent the user from logging out after password change
            update_session_auth_hash(request, password_change_form.user)

            return redirect('index')
    else:
        password_change_form = PasswordChangeForm(user=app_user)

    return render(request, 'social_media/change_password.html', {'password_change_form': password_change_form})


@login_required(login_url='/login/')
def user_logout(request):
    '''
    Handle user log out
    '''
    logout(request)

    return redirect('login')


@never_cache
def profile(request, username):
    '''
    User profile page
    '''
    # get the requested user
    requested_user = None
    try:
        requested_user = AppUser.objects.get(username=username)
    except AppUser.DoesNotExist:
        # requested user does not exist
        raise Http404

    context = {}

    # input profile user details
    context['id'] = requested_user.pk
    context['username'] = requested_user.username
    context['email'] = requested_user.email
    context['profile_image_url'] = requested_user.profile_image.url
    context['is_own_profile'] = False
    context['is_authenticated'] = False

    # if user is logged in
    app_user = request.user
    if app_user.is_authenticated:
        context['is_authenticated'] = True
        context['is_own_profile'] = app_user.pk == requested_user.pk

        # get the relationship between the logged in user and the requested user
        try:
            relationship = None
            # make sure user1 id is less then user2 id before query
            if app_user.pk < requested_user.pk:
                relationship = UserRelationship.objects.get(
                    user1=app_user.pk, user2=requested_user.pk)
                context['relation_type'] = 'sender' if relationship.relation_type == 'pending_user1_user2' else 'receiver'
            else:
                relationship = UserRelationship.objects.get(
                    user1=requested_user.pk, user2=app_user.pk)
                context['relation_type'] = 'sender' if relationship.relation_type == 'pending_user2_user1' else 'receiver'

            context['is_friend'] = relationship.relation_type == 'friends'

            # overwrite relation_type to 'friends' if they are friends
            if context['is_friend']:
                context['relation_type'] = 'friends'

        except UserRelationship.DoesNotExist:
            # if no UserRelationship record found, means they are not friend
            context['is_friend'] = False
            context['relation_type'] = 'not_friend'

    return render(request, 'social_media/profile.html', context)


@login_required(login_url='/login/')
def search_user(request):
    '''
    User search result page
    '''
    app_user = request.user

    if request.method == 'GET':
        search_input = request.GET.get('query')
        # default page number to 1
        page_number = request.GET.get('page', 1)
        context = {}

        if search_input:
            # if input is provided
            results = []
            # get users where email or username contain the input (exclude the logged in user)
            user_results = AppUser.objects.exclude(pk=app_user.pk).filter(
                Q(email__icontains=search_input) | Q(username__icontains=search_input)).order_by('username')

            for user in user_results:
                results.append({
                    'id': user.pk,
                    'profile_image_url': user.profile_image.url,
                    'username': user.username
                })
                
            # pagination
            paginator = Paginator(results, 5)
            
            try:
                paginated_results = paginator.page(page_number)
            except PageNotAnInteger:
                # if page_number is not integer
                paginated_results = paginator.page(1)
            except EmptyPage:
                # return the last page if page number is out of range
                paginated_results = paginator.page(paginator.num_pages)

            context['paginated_results'] = paginated_results
            context['query'] = search_input
        else:
            raise Http404

    return render(request, 'social_media/search_result.html', context)


@login_required(login_url='/login/')
def profile_update(request):
    '''
    Update profile detail page
    '''
    app_user = request.user

    if request.method == 'POST':
        profile_update_form = ProfileUpdateForm(
            request.POST, request.FILES, instance=app_user)

        # if the input is valid
        if profile_update_form.is_valid():
            # update the instance
            profile_update_form.save()

            # redirect to profile page
            return redirect('profile', username=profile_update_form.cleaned_data['username'])
    else:
        profile_update_form = ProfileUpdateForm(
            request.POST or None, instance=app_user)

    return render(request, 'social_media/update_profile.html', {'profile_update_form': profile_update_form})


@login_required(login_url='/login/')
def friend_list(request, username):
    '''
    Friend list page
    '''
    app_user = request.user

    # check if the requested user exist
    requested_user = None
    try:
        requested_user = AppUser.objects.get(username=username)
    except AppUser.DoesNotExist:
        raise Http404

    # get a list of requested user's friends
    context = {}
    friends = []
    relationships = UserRelationship.objects.filter(
        Q(user1=requested_user) | Q(user2=requested_user), relation_type='friends')

    for relationship in relationships:
        if requested_user.pk == relationship.user1.pk:
            friends.append({
                'id': relationship.user2.pk,
                'profile_image_url': relationship.user2.profile_image.url,
                'username': relationship.user2.username,
            })
        else:
            friends.append({
                'id': relationship.user1.pk,
                'profile_image_url': relationship.user1.profile_image.url,
                'username': relationship.user1.username,
            })

    # sort the list of friends by their username
    friends.sort(key=lambda x: x.get('username'))

    context['friends'] = friends
    context['is_own'] = app_user.pk == requested_user.pk
    context['requested_user_username'] = requested_user.username

    return render(request, 'social_media/friend_list.html', context)


@login_required(login_url='/login/')
def friend_requests_list(request):
    '''
    Friend request list page
    '''
    app_user = request.user

    # get UserRelationship where (user1=app_user AND relation_type='pending_user2_user1') OR
    # (user2=app_user AND relation_type='pending_user2_user1')
    relationships = UserRelationship.objects.filter((Q(user1=app_user) & Q(
        relation_type='pending_user2_user1')) | (Q(user2=app_user) & Q(relation_type='pending_user1_user2'))).order_by('-date_modified')

    # list of users that send the app user friend request
    friend_requests = []
    for relationship in relationships:
        if app_user.pk == relationship.user1.pk:
            friend_requests.append({
                'id': relationship.user2.pk,
                'profile_image_url': relationship.user2.profile_image.url,
                'username': relationship.user2.username,
            })
        else:
            friend_requests.append({
                'id': relationship.user1.pk,
                'profile_image_url': relationship.user1.profile_image.url,
                'username': relationship.user1.username,
            })

    return render(request, 'social_media/friend_request_list.html', {'friend_requests': friend_requests})