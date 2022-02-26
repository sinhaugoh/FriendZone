from django.shortcuts import render, redirect
from django.http import Http404, HttpResponse
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.views.decorators.cache import never_cache
from django.db.models import Q
from django.contrib.auth.forms import PasswordChangeForm

from .models import AppUser, UserRelationship, Post

from .forms import RegistrationForm, LoginForm, ProfileUpdateForm

# Create your views here.
def index(request):
    app_user = request.user

    if app_user.is_authenticated:
        # authenticated

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
                
        # create a list of posts
        posts = Post.objects.filter(owner__in = post_users).order_by('-date_created')
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
            password_change_form = PasswordChangeForm(
                data=request.POST, user=app_user)

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


def profile(request, username):
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


def search_user(request):
    app_user = request.user

    if app_user.is_authenticated:
        if request.method == 'GET':
            search_input = request.GET.get('query')
            context = {}

            if search_input:
                # if there is input
                results = []
                # get users where email or username contain the input (exclude the logged in user)
                user_results = AppUser.objects.exclude(pk=app_user.pk).filter(
                    Q(email__icontains=search_input) | Q(username__icontains=search_input))

                for user in user_results:
                    results.append({
                        'id': user.pk,
                        'profile_image_url': user.profile_image.url,
                        'username': user.username
                    })
                    # temp_dict = {
                    #     'id': user.id,
                    #     'profile_image_url': user.profile_image.url,
                    #     'username': user.username,
                    #     'is_own': app_user.pk == user.pk,
                    # }
                    # try:
                    #     relationship = None
                    #     if app_user.pk < user.pk:
                    #         # get UserRelationship where user1 is app_user and user2 is user
                    #         relationship = UserRelationship.objects.get(
                    #             user1=app_user, user2=user)
                    #         temp_dict['relation_type'] = 'sender' if relationship.relation_type == 'pending_user1_user2' else 'receiver'
                    #     else:
                    #         # get UserRelationship where user1 is user and user2 is app_user
                    #         relationship = UserRelationship.objects.get(
                    #             user1=user, user2=app_user)
                    #         temp_dict['relation_type'] = 'sender' if relationship.relation_type == 'pending_user2_user1' else 'receiver'

                    #     temp_dict['is_friend'] = relationship.relation_type == 'friends'
                    #     # overwrite relation_type to 'friends' if they are friends
                    #     if temp_dict['is_friend']:
                    #         temp_dict['relation_type'] = 'friends'

                    # except UserRelationship.DoesNotExist:
                    #     # if no relationship (not friend)
                    #     temp_dict['is_friend'] = False
                    #     temp_dict['relation_type'] = 'not_friend'

                    # append the result at the end of the loop
                    # results.append(temp_dict)

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
                profile_update_form.save()

                return redirect('profile', username=profile_update_form.cleaned_data['username'])
        else:
            profile_update_form = ProfileUpdateForm(
                request.POST or None, instance=user)

        return render(request, 'social_media/update_profile.html', {'profile_update_form': profile_update_form})
    else:
        # not authenticated
        return redirect('login')


def friend_list(request, username):
    app_user = request.user

    if app_user.is_authenticated:
        requested_user = None
        try:
            requested_user = AppUser.objects.get(username=username)
        except AppUser.DoesNotExist:
            raise Http404

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

        # sort friends by username
        friends.sort(key=lambda x: x.get('username'))

        context['friends'] = friends
        context['is_own'] = app_user.pk == requested_user.pk
        context['requested_user_username'] = requested_user.username
        return render(request, 'social_media/friend_list.html', context)
    else:
        # TODO: can be changed so that people that are not authenticated can view certain info
        # not authenticated
        return redirect('login')


def friend_requests_list(request):
    app_user = request.user

    if app_user.is_authenticated:
        # friend_requests = UserRelationship.objects.filter(Q(user1=app_user) | Q(user2=app_user), relation_type__startswith='pending')
        # friend_requests = UserRelationship.objects.filter(user1=app_user, relation_type='pending_user2_user1').filter(user2=app_user, relation_type='pending_user1_user2')

        # get UserRelationship where (user1=app_user AND relation_type='pending_user2_user1') OR
        # (user2=app_user AND relation_type='pending_user2_user1')
        relationships = UserRelationship.objects.filter((Q(user1=app_user) & Q(
            relation_type='pending_user2_user1')) | (Q(user2=app_user) & Q(relation_type='pending_user1_user2'))).order_by('-date_modified')

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
    else:
        # not authenticated
        return redirect('login')
