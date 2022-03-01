from django.test import TestCase
from django.urls import reverse

from ..model_factories import *

USER_PASSWORD = 'Asdf1234'


class ChatRoomViewTest(TestCase):
    def setUp(self):
        super().setUp()
        self.user1 = AppUserFactory.create()
        self.user2 = AppUserFactory.create()
        self.user3 = AppUserFactory.create()
        self.url = reverse('chat_room', kwargs={
                           'chat_target_id': self.user2.pk})

        # make user1 and user2 friend
        UserRelationshipFactory.create(
            user1=self.user1, user2=self.user2, relation_type='friends')

        # make some messages
        self.message1 = Message.objects.create(
            sender=self.user1, receiver=self.user2)

        # log user1 in
        self.client.login(email=self.user1.email, password=USER_PASSWORD)

    def tearDown(self):
        super().tearDown()
        AppUser.objects.all().delete()
        UserRelationship.objects.all().delete()
        Message.objects.all().delete()
        AppUserFactory.reset_sequence(0)
        UserRelationshipFactory.reset_sequence(0)

    def test_urlIsWorking(self):
        response = self.client.get('/chat/{}/'.format(self.user2.pk))

        self.assertEqual(response.status_code, 200)

    def test_urlByNameIsWorking(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

    def test_redirectIfNotAuthenticated(self):
        # log user1 out
        self.client.logout()

        response = self.client.get(self.url)

        self.assertRedirects(
            response, '/login/?next=/chat/{}/'.format(self.user2.pk))

    def test_loggedInUsesCorrectTemplate(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'chat/chat_room.html')

    def test_invalidFriendIdReturn400(self):
        response = self.client.get(
            reverse('chat_room', kwargs={'chat_target_id': self.user3.pk}))

        self.assertEqual(response.status_code, 400)

    def test_validRequestReturnCorrectResult(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['messages'], [{
            'content': self.message1.content,
            'sender': {
                'profile_image_path': self.message1.sender.profile_image.url,
                'username': self.message1.sender.username
            },
            'receiver': {
                'profile_image_path': self.message1.receiver.profile_image.url,
                'username': self.message1.receiver.username
            },
            'date_created': self.message1.date_created
        }])
        self.assertEqual(response.context['target_user'], {
            'username': self.user2.username,
            'profile_image_path': self.user2.profile_image.url
        })
