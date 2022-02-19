from django.http import HttpResponse
import json

from .models import UserRelationship, AppUser


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
            # check if AppUser with the requested_user_id exist
            requested_user = None
            try:
                # exclude the app_user because app_user cannot be the requested_user
                requested_user = AppUser.objects.exclude(pk=app_user.pk).get(pk=requested_user_id)
            except AppUser.DoesNotExist:
                # invalid requested_user_id
                payload['response_msg'] = 'Invalid request id.'
                return HttpResponse(json.dumps(payload), content_type='application/json')

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

    return HttpResponse(json.dumps(payload), content_type='application/json')

def cancel_friend_request(request):
    app_user = request.user
    payload = {}
    
    if app_user.is_authenticated and request.method == 'POST':
        data = json.loads(request.body)
        requested_user_id = data.get('id', None)
        
        if requested_user_id:
            # check if AppUser with the requested_user_id exist
            requested_user = None
            try:
                # exclude the app_user because app_user cannot be the requested_user
                requested_user = AppUser.objects.exclude(pk=app_user.pk).get(pk=requested_user_id)
            except AppUser.DoesNotExist:
                # invalid requested_user_id
                payload['response_msg'] = 'Invalid request id.'
                return HttpResponse(json.dumps(payload), content_type='application/json')

            user1, user2 = determine_user1_and_user2_in_user_relationship(app_user, requested_user)
            
            try:
                # if found, delete the relationship
                relationship = UserRelationship.objects.get(user1=user1, user2=user2, relation_type='pending_user1_user2' if app_user.pk == user1.pk else 'pending_user2_user1')
                relationship.delete()
                
                payload['response_msg'] = 'Friend request cancelled.'
            except UserRelationship.DoesNotExist:
                # if not found, invalid request
                payload['response_msg'] = 'Invalid request.'
    else:
        # not authenticated
        payload['response_msg'] = 'You are not authenticated.'
        
    return HttpResponse(json.dumps(payload), content_type='application/json')