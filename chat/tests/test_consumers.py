from channels.testing import WebsocketCommunicator
from channels.routing import URLRouter
from django.test import TransactionTestCase
import chat.routing
from asgiref.sync import sync_to_async

from ..model_factories import *

class ChatWebSocketTest(TransactionTestCase):
    def setUp(self):
        self.user1 = AppUserFactory.create()
        self.user2 = AppUserFactory.create()
        
        
    def tearDown(self):
        Message.objects.all().delete()
        AppUser.objects.all().delete()
    
    async def test_canConnect(self):
        room_name = '{}_{}'.format(self.user1.pk, self.user2.pk)
        application = URLRouter(chat.routing.websocket_urlpatterns)
        communicator = WebsocketCommunicator(application, 'ws/{}/'.format(room_name))
        
        # connect the websocket
        connected, _ = await communicator.connect()
        
        self.assertTrue(connected)

        await communicator.disconnect()
        
    async def test_canSendAndReceiveMessage(self):
        room_name = '{}_{}'.format(self.user1.pk, self.user2.pk)
        application = URLRouter(chat.routing.websocket_urlpatterns)
        communicator = WebsocketCommunicator(application, 'ws/{}/'.format(room_name))
        communicator.scope['user'] = self.user1.email
        
        # connect the websocket
        await communicator.connect()

        message = {
                'message': 'Test message',
                'username': 'test1',
                'profile_image_path': ''
        }
        
        await communicator.send_json_to(message)
        response = await communicator.receive_json_from()
        
        self.assertEqual(response, message)
        
        await communicator.disconnect()
        
    async def test_messageInstanceIsStoredInDatabaseAfterAMessageIsSent(self):
        room_name = '{}_{}'.format(self.user1.pk, self.user2.pk)
        application = URLRouter(chat.routing.websocket_urlpatterns)
        communicator = WebsocketCommunicator(application, 'ws/{}/'.format(room_name))
        communicator.scope['user'] = self.user1.email
        
        # connect the websocket
        await communicator.connect()

        message = {
                'message': 'Test message',
                'username': 'test1',
                'profile_image_path': ''
        }
        
        # send message
        await communicator.send_json_to(message)
        # receive message
        await communicator.receive_json_from()
        
        messages = await sync_to_async(list)(Message.objects.all())
        
        # check message count
        self.assertEqual(len(messages), 1)
        
        await communicator.disconnect()