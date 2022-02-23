from django.db.models import Q
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework import generics, status, permissions
import json

from .models import UserRelationship, AppUser, Post
from .forms import PostForm
from .serializers import FriendListSerializer, PostSerializer


def determine_user1_and_user2_in_user_relationship(user1, user2):
    '''determine which user should be the user1 and which should be the user2.

    Current logic:

    user1 = user with smaller pk

    user2 = user with larger pk
    '''
    if user1.pk < user2.pk:
        return (user1, user2)
    else:
        return (user2, user1)


def send_friend_request(request):
    app_user = request.user

    if app_user.is_authenticated and request.method == 'POST':
        data = json.loads(request.body)
        requested_user_id = data.get('id', None)
        payload = {}
        
        if requested_user_id:
            # check if the requested_user exist
            requested_user = None
            try:
                # exclude the app_user because app_user cannot be the requested_user
                requested_user = AppUser.objects.exclude(pk=app_user.pk).get(pk=requested_user_id)
            except AppUser.DoesNotExist:
                # invalid requested_user_id
                payload['response_msg'] = 'Invalid request id.'
                return JsonResponse(payload)

            # determine user1 and user2 in UserRelationship
            user1, user2 = determine_user1_and_user2_in_user_relationship(
                app_user, requested_user)

            # check if the relationship between user1 and user2 already exist
            if not UserRelationship.objects.filter(user1=user1, user2=user2).exists():
                new_relationship = UserRelationship(
                    user1=user1, user2=user2, relation_type='pending_user1_user2' if app_user.pk == user1.pk else 'pending_user2_user1')
                new_relationship.save()
                payload['response_msg'] = 'Friend request sent.'
            else:
                payload['response_msg'] = 'Invalid request.'
        else:
            payload['response_msg'] = 'Requested user not found'
    else:
        # not authenticated
        payload['response_msg'] = 'You are not authenticated.'

    return JsonResponse(payload)

def cancel_friend_request(request):
    app_user = request.user
    payload = {}
    
    if app_user.is_authenticated and request.method == 'POST':
        data = json.loads(request.body)
        requested_user_id = data.get('id', None)
        
        if requested_user_id:
            # check if the requested_user exist
            requested_user = None
            try:
                # exclude the app_user because app_user cannot be the requested_user
                requested_user = AppUser.objects.exclude(pk=app_user.pk).get(pk=requested_user_id)
            except AppUser.DoesNotExist:
                # invalid requested_user_id
                payload['response_msg'] = 'Invalid request id.'
                return JsonResponse(payload)

            user1, user2 = determine_user1_and_user2_in_user_relationship(app_user, requested_user)
            
            try:
                # if the relationship is valid (current user is the friend request sender)
                relationship = UserRelationship.objects.get(user1=user1, user2=user2, relation_type='pending_user1_user2' if app_user.pk == user1.pk else 'pending_user2_user1')
                relationship.delete()
                
                payload['response_msg'] = 'Friend request cancelled.'
            except UserRelationship.DoesNotExist:
                # if the relationship is not found
                payload['response_msg'] = 'Invalid request.'
    else:
        # not authenticated
        payload['response_msg'] = 'You are not authenticated.'
        
    return JsonResponse(payload)

def accept_friend_request(request):
    app_user = request.user
    payload = {}
    
    if app_user.is_authenticated and request.method == 'POST':
        data = json.loads(request.body)
        requested_user_id = data.get('id', None)
        
        if requested_user_id:
            # check if the requested_user exist
            requested_user = None
            try:
                # exclude the app_user because app_user cannot be the requested_user
                requested_user = AppUser.objects.exclude(pk=app_user.pk).get(pk=requested_user_id)
            except AppUser.DoesNotExist:
                # invalid requested_user_id
                payload['response_msg'] = 'Invalid request id.'
                return JsonResponse(payload)

            user1, user2 = determine_user1_and_user2_in_user_relationship(app_user, requested_user)
            
            try:
                # if the relationship is valid (current user is the friend request receiver)
                relationship = UserRelationship.objects.get(user1=user1, user2=user2, relation_type='pending_user2_user1' if app_user.pk == user1.pk else 'pending_user1_user2')
                # accept the friend request
                relationship.accept_friend_request()
                
                payload['response_msg'] = 'Friend request accepted.'
            except UserRelationship.DoesNotExist:
                # if the relationship is not found
                payload['response_msg'] = 'Invalid request.'
    else:
        # not authenticated
        payload['response_msg'] = 'You are not authenticated.'
        
    return JsonResponse(payload)

def decline_friend_request(request):
    app_user = request.user
    payload = {}
    
    if app_user.is_authenticated and request.method == 'POST':
        data = json.loads(request.body)
        requested_user_id = data.get('id', None)
        
        if requested_user_id:
            # check if the requested_user exist
            requested_user = None
            try:
                # exclude the app_user because app_user cannot be the requested_user
                requested_user = AppUser.objects.exclude(pk=app_user.pk).get(pk=requested_user_id)
            except AppUser.DoesNotExist:
                # invalid requested_user_id
                payload['response_msg'] = 'Invalid request id.'
                return JsonResponse(payload)

            user1, user2 = determine_user1_and_user2_in_user_relationship(app_user, requested_user)
            
            try:
                # if the relationship is valid (current user is the friend request receiver)
                relationship = UserRelationship.objects.get(user1=user1, user2=user2, relation_type='pending_user2_user1' if app_user.pk == user1.pk else 'pending_user1_user2')
                relationship.delete()
                
                payload['response_msg'] = 'Friend request declined.'
            except UserRelationship.DoesNotExist:
                # if the relationship is not found
                payload['response_msg'] = 'Invalid request.'
    else:
        # not authenticated
        payload['response_msg'] = 'You are not authenticated.'
        
    return JsonResponse(payload)

def remove_friend(request):
    app_user = request.user
    payload = {}
    
    if app_user.is_authenticated and request.method == 'POST':
        data = json.loads(request.body)
        requested_user_id = data.get('id', None)
        
        if requested_user_id:
            # check if the requested_user exist
            requested_user = None
            try:
                # exclude the app_user because app_user cannot be the requested_user
                requested_user = AppUser.objects.exclude(pk=app_user.pk).get(pk=requested_user_id)
            except AppUser.DoesNotExist:
                # invalid requested_user_id
                payload['response_msg'] = 'Invalid request id.'
                return JsonResponse(payload)

            user1, user2 = determine_user1_and_user2_in_user_relationship(app_user, requested_user)
            
            try:
                # if the relationship is valid (current user and requested user are friends)
                relationship = UserRelationship.objects.get(user1=user1, user2=user2,relation_type='friends')
                relationship.delete()
                
                payload['response_msg'] = 'Friend removed.'
            except UserRelationship.DoesNotExist:
                # if the relationship is not found
                payload['response_msg'] = 'Invalid request.'
    else:
        # not authenticated
        payload['response_msg'] = 'You are not authenticated.'
        
    return JsonResponse(payload)

def create_post(request):
    app_user = request.user
    payload = {}
    
    # check if user is authenticated
    if not app_user.is_authenticated:
        payload['response_msg'] = 'You are not authenticated.'
        return JsonResponse(payload, status=401)
        
    # check if the request method is POST
    if request.method != 'POST':
        payload['response_msg'] = 'Invalid request.'
        return JsonResponse(payload, status=400)
    
    
    post_form = PostForm(request.POST, request.FILES)
    if post_form.is_valid():
        # create the instance if the input is valid
        post = post_form.save(commit=False)
        post.owner = app_user
        post.save()
        
        payload['response_msg'] = 'Post created.'
        # return post data
        payload['data'] = {
            'owner_username': post.owner.username,
            'owner_profile_image_path': post.owner.profile_image.url,
            'post_text': post.text,
            'post_image_path': None if post_form.cleaned_data['image'] is None else post.image.url,
            'post_date_created': post.date_created
        }
        return JsonResponse(payload, status=201)
    else:
        payload['response_msg'] = post_form.errors
        return JsonResponse(payload, status=400)
    
    
###################### DRF ##################
class UserPostList(generics.ListAPIView):
    serializer_class = PostSerializer
    lookup_field = 'username'
    
    def get_queryset(self):
        username = self.kwargs['username']
        
        return Post.objects.filter(owner__username=username)
    

############# NOT USED ######################

class FriendList(generics.ListAPIView):
    serializer_class = FriendListSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'username'
    
    def get_queryset(self):
        requested_username = self.kwargs['username']
        app_user = self.request.user
        
        if app_user.is_authenticated:
            requested_user = None
            # get the requested user
            try:
                requested_user = AppUser.objects.get(username=requested_username)
            except AppUser.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
            
            friends = []

            # get all relationships related to the requested user
            relationships = UserRelationship.objects.filter(
                Q(user1=requested_user) | Q(user2=requested_user), relation_type='friends')
            
            # filter and get a list of requested user's friends
            for relationship in relationships:
                if requested_user.pk == relationship.user1.pk:
                    friends.append(relationship.user2)
                else:
                    friends.append(relationship.user1)

            # sort friends by username
            friends.sort(key=lambda x: x.username)
            
            return friends
    