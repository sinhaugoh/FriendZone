from django.db.models import Q
from django.http import HttpResponseBadRequest
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from social_media.models import UserRelationship, AppUser
from .models import Message


def create_room_name(user1_pk, user2_pk):
    if user1_pk < user2_pk:
        return '{}_{}'.format(str(user1_pk), str(user2_pk))
    else:
        return '{}_{}'.format(str(user2_pk), str(user1_pk))


@login_required(login_url='/login/')
def chat_room(request, chat_target_id):
    app_user = request.user

    # get user1_pk and user2_pk for UserRelationship
    user1_pk = min(app_user.pk, chat_target_id)
    user2_pk = max(app_user.pk, chat_target_id)

    context = {}
    # check if the app user and target user are friends
    if UserRelationship.objects.filter(user1__pk=user1_pk, user2__pk=user2_pk, relation_type='friends').exists():
        context['room_name'] = create_room_name(user1_pk, user2_pk)

        # get message history
        messages = Message.objects.filter(Q(sender__pk=user1_pk, receiver__pk=user2_pk) | Q(
            sender__pk=user2_pk, receiver__pk=user1_pk))

        message_list = []
        for message in messages:
            message_list.append({
                'content': message.content,
                'sender': {
                    'profile_image_path': message.sender.profile_image.url,
                    'username': message.sender.username
                },
                'receiver': {
                    'profile_image_path': message.receiver.profile_image.url,
                    'username': message.receiver.username
                },
                'date_created': message.date_created
            })

        context['messages'] = message_list
        
        # get target user info
        target_user = AppUser.objects.get(pk=chat_target_id)
        context['target_user'] = {
            'username': target_user.username,
            'profile_image_path': target_user.profile_image.url
        }

    else:
        # the app user and targer user is not friend
        return HttpResponseBadRequest('Invalid request')

    return render(request, 'chat/chat_room.html', context)
