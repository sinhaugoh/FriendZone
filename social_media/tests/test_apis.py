from django.test import override_settings
import shutil
import tempfile
from rest_framework.test import APITestCase
from django.urls import reverse
import json

from ..model_factories import *


MEDIA_ROOT = tempfile.mkdtemp()
TEST_SERVER_DOMAIN = 'http://testserver'
USER_PASSWORD = 'Asdf1234'
INVALID_USER_PK = 999999


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class UserPostListTest(APITestCase):
    def setUp(self):
        super().setUp()
        self.user1 = AppUserFactory.create()
        self.post1 = PostFactory.create(owner=self.user1)

        self.good_url = reverse('user_posts', kwargs={
            'username': self.user1.username})
        self.bad_url = reverse('user_posts', kwargs={
                               'username': 'BAD_USERNAME'})

    def tearDown(self):
        super().tearDown()
        AppUser.objects.all().delete()
        Post.objects.all().delete()
        AppUserFactory.reset_sequence(0)
        PostFactory.reset_sequence(0)

        # remove test image temp folder
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)

    def test_validUsernameReturnSuccess(self):
        response = self.client.get(self.good_url)
        self.assertEqual(response.status_code, 200)

    def test_validUsernameReturnCorrectResult(self):
        response = self.client.get(self.good_url)
        data = json.loads(response.content)

        self.assertEqual(len(data), 1)
        self.assertEqual(data, [{
            'image': TEST_SERVER_DOMAIN + self.post1.image.url,
            'text': self.post1.text,
            'date_created': self.post1.date_created.strftime("%Y-%m-%d %H:%M")
        }, ])

    def test_validUsernameWithNoPostReturnSuccess(self):
        # remove default posts
        Post.objects.all().delete()

        response = self.client.get(self.good_url)
        self.assertEqual(response.status_code, 200)

    def test_validUsernameWithNoPostReturnCorrectResult(self):
        # remove default posts
        Post.objects.all().delete()

        response = self.client.get(self.good_url)
        data = json.loads(response.content)

        self.assertEqual(len(data), 0)
        self.assertEqual(data, [])

    def test_invalidUsernameReturnCorrectResult(self):
        response = self.client.get(self.bad_url)
        data = json.loads(response.content)
        self.assertEqual(data, [])


# TODO: Implement
@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class CreatePostTest(APITestCase):
    def setUp(self):
        super().setUp()
        self.user1 = AppUserFactory.create()
        self.url = reverse('create_post')
        self.text = 'Test status text'

        # log user1 in
        self.client.login(email=self.user1.email, password=USER_PASSWORD)

    def tearDown(self):
        super().tearDown()
        AppUser.objects.all().delete()
        Post.objects.all().delete()
        AppUserFactory.reset_sequence(0)
        PostFactory.reset_sequence(0)

        # remove test image temp folder
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)

    def test_unauthenticatedRequestReturn403(self):
        # log user1 out
        self.client.logout()

        response = self.client.post(self.url, {'text': self.text})

        self.assertEqual(response.status_code, 403)

    def test_unauthenticatedRequestReturnCorrectKeys(self):
        # log user1 out
        self.client.logout()

        response = self.client.post(self.url, {'text': self.text})
        data = json.loads(response.content)

        self.assertTrue('detail' in data.keys())

    def test_validRequestReturnSuccess(self):
        response = self.client.post(self.url, {'text': self.text})
        self.assertEqual(response.status_code, 201)

    def test_validRequestReturnCorrectResult(self):
        response = self.client.post(self.url, {'text': self.text})
        data = json.loads(response.content)

        self.assertEqual(data, {
            'response_msg': 'Post created.',
            'data': {
                'owner_username': self.user1.username,
                'owner_profile_image_path': self.user1.profile_image.url,
                'post_text': self.text,
                'post_image_path': None,
                'post_date_created': data['data']['post_date_created']
            }
        })

    def test_invalidRequestWithNoTextAndImageReturn400(self):
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 400)

    def test_invalidRequestWithNoTextAndImageReturnCorrectKeys(self):
        response = self.client.post(self.url)
        data = json.loads(response.content)

        self.assertTrue('response_msg' in data.keys())


class SendFriendRequestTest(APITestCase):
    def setUp(self):
        super().setUp()
        self.user1 = AppUserFactory.create()
        self.user2 = AppUserFactory.create()
        # log user1 in
        self.client.login(email=self.user1.email, password=USER_PASSWORD)

        self.url = reverse('send_friend_request')

    def tearDown(self):
        super().tearDown()
        AppUser.objects.all().delete()
        UserRelationship.objects.all().delete()
        AppUserFactory.reset_sequence(0)
        UserRelationshipFactory.reset_sequence(0)

    def test_unauthenticatedRequestReturn403(self):
        # log user1 out
        self.client.logout()

        response = self.client.post(self.url, {'id': self.user2.pk})
        self.assertEqual(response.status_code, 403)

    def test_unauthenticatedRequestReturnCorrentKeys(self):
        # log user1 out
        self.client.logout()

        response = self.client.post(self.url, {'id': self.user2.pk})
        data = json.loads(response.content)

        self.assertTrue('detail' in data.keys())

    def test_validRequestReturn204Success(self):
        response = self.client.post(self.url, {'id': self.user2.pk})
        self.assertEqual(response.status_code, 204)

    def test_validRequestReturnCorrectRelationship(self):
        response = self.client.post(self.url, {'id': self.user2.pk})

        # make sure user1 has sent a friend request to user2
        relationship_exist = UserRelationship.objects.filter(
            user1=self.user1, user2=self.user2, relation_type='pending_user1_user2').exists()
        self.assertTrue(relationship_exist)

    def test_invalidRequestWithInvalidDataReturn400(self):
        response = self.client.post(self.url, {'id': INVALID_USER_PK})
        self.assertEqual(response.status_code, 400)

    def test_invalidRequestWithInvalidDataReturnCorrectKeys(self):
        response = self.client.post(self.url, {'id': INVALID_USER_PK})
        data = json.loads(response.content)
        self.assertTrue('detail' in data.keys())

    def test_invalidRequestWithNoDataReturn400(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 400)

    def test_invalidRequestWithNoDataReturnCorrectKeys(self):
        response = self.client.post(self.url)
        data = json.loads(response.content)
        self.assertTrue('detail' in data.keys())

    def test_invalidRequestWithWrongRelationTypeReturn400(self):
        # if user1 and user2 are friends, then send friend request should
        # return 400
        UserRelationshipFactory.create(
            user1=self.user1, user2=self.user2, relation_type='friends')

        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 400)

    def test_invalidRequestWithWrongRelationTypeReturnCorrectKeys(self):
        # if user1 and user2 are friends, then send friend request should
        # return 400
        UserRelationshipFactory.create(
            user1=self.user1, user2=self.user2, relation_type='friends')

        response = self.client.post(self.url)
        data = json.loads(response.content)
        self.assertTrue('detail' in data.keys())


class CancelFriendRequestTest(APITestCase):
    def setUp(self):
        super().setUp()
        self.user1 = AppUserFactory.create()
        self.user2 = AppUserFactory.create()

        # user1 sent user2 a friend request
        self.user_relationship = UserRelationshipFactory.create(
            user1=self.user1, user2=self.user2, relation_type='pending_user1_user2')
        # log user1 in
        self.client.login(email=self.user1.email, password=USER_PASSWORD)

        self.url = reverse('cancel_friend_request')

    def tearDown(self):
        super().tearDown()
        AppUser.objects.all().delete()
        UserRelationship.objects.all().delete()
        AppUserFactory.reset_sequence(0)
        UserRelationshipFactory.reset_sequence(0)

    def test_unauthenticatedRequestReturn403(self):
        # log user1 out
        self.client.logout()

        response = self.client.post(self.url, {'id': self.user2.pk})
        self.assertEqual(response.status_code, 403)

    def test_unauthenticatedRequestReturnCorrentKeys(self):
        # log user1 out
        self.client.logout()

        response = self.client.post(self.url, {'id': self.user2.pk})
        data = json.loads(response.content)

        self.assertTrue('detail' in data.keys())

    def test_validRequestReturn204Success(self):
        response = self.client.post(self.url, {'id': self.user2.pk})
        self.assertEqual(response.status_code, 204)

    def test_validRequestReturnCorrectRelationship(self):
        response = self.client.post(self.url, {'id': self.user2.pk})

        # make sure no relationship found between user1 and user2
        relationship_exist = UserRelationship.objects.filter(
            user1=self.user1, user2=self.user2).exists()
        self.assertTrue(not relationship_exist)

    def test_invalidRequestWithInvalidDataReturn400(self):
        response = self.client.post(self.url, {'id': INVALID_USER_PK})
        self.assertEqual(response.status_code, 400)

    def test_invalidRequestWithInvalidDataReturnCorrectKeys(self):
        response = self.client.post(self.url, {'id': INVALID_USER_PK})
        data = json.loads(response.content)
        self.assertTrue('detail' in data.keys())

    def test_invalidRequestWithNoDataReturn400(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 400)

    def test_invalidRequestWithNoDataReturnCorrectKeys(self):
        response = self.client.post(self.url)
        data = json.loads(response.content)
        self.assertTrue('detail' in data.keys())

    def test_invalidRequestWithWrongRelationTypeReturn400(self):
        # if user1 didn't send user2 a friend request, then cancel friend request should
        # return 400
        self.user_relationship.delete()

        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 400)

    def test_invalidRequestWithWrongRelationTypeReturnCorrectKeys(self):
        # if user1 didn't send user2 a friend request, then cancel friend request should
        # return 400
        self.user_relationship.delete()

        response = self.client.post(self.url)
        data = json.loads(response.content)
        self.assertTrue('detail' in data.keys())


class AcceptFriendRequestTest(APITestCase):
    def setUp(self):
        super().setUp()
        self.user1 = AppUserFactory.create()
        self.user2 = AppUserFactory.create()

        # user2 sent user1 a friend request
        self.user_relationship = UserRelationshipFactory.create(
            user1=self.user1, user2=self.user2, relation_type='pending_user2_user1')
        # log user1 in
        self.client.login(email=self.user1.email, password=USER_PASSWORD)

        self.url = reverse('accept_friend_request')

    def tearDown(self):
        super().tearDown()
        AppUser.objects.all().delete()
        UserRelationship.objects.all().delete()
        AppUserFactory.reset_sequence(0)
        UserRelationshipFactory.reset_sequence(0)

    def test_unauthenticatedRequestReturn403(self):
        # log user1 out
        self.client.logout()

        response = self.client.post(self.url, {'id': self.user2.pk})
        self.assertEqual(response.status_code, 403)

    def test_unauthenticatedRequestReturnCorrentKeys(self):
        # log user1 out
        self.client.logout()

        response = self.client.post(self.url, {'id': self.user2.pk})
        data = json.loads(response.content)

        self.assertTrue('detail' in data.keys())

    def test_validRequestReturn204Success(self):
        response = self.client.post(self.url, {'id': self.user2.pk})
        self.assertEqual(response.status_code, 204)

    def test_validRequestReturnCorrectRelationship(self):
        response = self.client.post(self.url, {'id': self.user2.pk})

        # make sure user1 and user2 are friends
        relationship_exist = UserRelationship.objects.filter(
            user1=self.user1, user2=self.user2, relation_type='friends').exists()
        self.assertTrue(relationship_exist)

    def test_invalidRequestWithInvalidDataReturn400(self):
        response = self.client.post(self.url, {'id': INVALID_USER_PK})
        self.assertEqual(response.status_code, 400)

    def test_invalidRequestWithInvalidDataReturnCorrectKeys(self):
        response = self.client.post(self.url, {'id': INVALID_USER_PK})
        data = json.loads(response.content)
        self.assertTrue('detail' in data.keys())

    def test_invalidRequestWithNoDataReturn400(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 400)

    def test_invalidRequestWithNoDataReturnCorrectKeys(self):
        response = self.client.post(self.url)
        data = json.loads(response.content)
        self.assertTrue('detail' in data.keys())

    def test_invalidRequestWithWrongRelationTypeReturn400(self):
        # if user2 didn't send user1 a friend request, then user1 shouldn't be able to
        # accept the non-existing friend request
        self.user_relationship.delete()

        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 400)

    def test_invalidRequestWithWrongRelationTypeReturnCorrectKeys(self):
        # if user2 didn't send user1 a friend request, then user1 shouldn't be able to
        # accept the non-existing friend request
        self.user_relationship.delete()

        response = self.client.post(self.url)
        data = json.loads(response.content)
        self.assertTrue('detail' in data.keys())


class DeclineFriendRequestTest(APITestCase):
    def setUp(self):
        super().setUp()
        self.user1 = AppUserFactory.create()
        self.user2 = AppUserFactory.create()

        # user2 sent user1 a friend request
        self.user_relationship = UserRelationshipFactory.create(
            user1=self.user1, user2=self.user2, relation_type='pending_user2_user1')
        # log user1 in
        self.client.login(email=self.user1.email, password=USER_PASSWORD)

        self.url = reverse('decline_friend_request')

    def tearDown(self):
        super().tearDown()
        AppUser.objects.all().delete()
        UserRelationship.objects.all().delete()
        AppUserFactory.reset_sequence(0)
        UserRelationshipFactory.reset_sequence(0)

    def test_unauthenticatedRequestReturn403(self):
        # log user1 out
        self.client.logout()

        response = self.client.post(self.url, {'id': self.user2.pk})
        self.assertEqual(response.status_code, 403)

    def test_unauthenticatedRequestReturnCorrentKeys(self):
        # log user1 out
        self.client.logout()

        response = self.client.post(self.url, {'id': self.user2.pk})
        data = json.loads(response.content)

        self.assertTrue('detail' in data.keys())

    def test_validRequestReturn204Success(self):
        response = self.client.post(self.url, {'id': self.user2.pk})
        self.assertEqual(response.status_code, 204)

    def test_validRequestReturnCorrectRelationship(self):
        response = self.client.post(self.url, {'id': self.user2.pk})

        # make sure no relationship record found between user1 and user2
        relationship_exist = UserRelationship.objects.filter(
            user1=self.user1, user2=self.user2).exists()
        self.assertTrue(not relationship_exist)

    def test_invalidRequestWithInvalidDataReturn400(self):
        response = self.client.post(self.url, {'id': INVALID_USER_PK})
        self.assertEqual(response.status_code, 400)

    def test_invalidRequestWithInvalidDataReturnCorrectKeys(self):
        response = self.client.post(self.url, {'id': INVALID_USER_PK})
        data = json.loads(response.content)
        self.assertTrue('detail' in data.keys())

    def test_invalidRequestWithNoDataReturn400(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 400)

    def test_invalidRequestWithNoDataReturnCorrectKeys(self):
        response = self.client.post(self.url)
        data = json.loads(response.content)
        self.assertTrue('detail' in data.keys())

    def test_invalidRequestWithWrongRelationTypeReturn400(self):
        # if user2 didn't send user1 a friend request, then user1 shouldn't be able to
        # decline the non-existing friend request
        self.user_relationship.delete()

        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 400)

    def test_invalidRequestWithWrongRelationTypeReturnCorrectKeys(self):
        # if user2 didn't send user1 a friend request, then user1 shouldn't be able to
        # decline the non-existing friend request
        self.user_relationship.delete()

        response = self.client.post(self.url)
        data = json.loads(response.content)
        self.assertTrue('detail' in data.keys())


class RemoveFriendTest(APITestCase):
    def setUp(self):
        super().setUp()
        self.user1 = AppUserFactory.create()
        self.user2 = AppUserFactory.create()

        # user1 and user2 are friends
        self.user_relationship = UserRelationshipFactory.create(
            user1=self.user1, user2=self.user2, relation_type='friends')
        # log user1 in
        self.client.login(email=self.user1.email, password=USER_PASSWORD)

        self.url = reverse('remove_friend')

    def tearDown(self):
        super().tearDown()
        AppUser.objects.all().delete()
        UserRelationship.objects.all().delete()
        AppUserFactory.reset_sequence(0)
        UserRelationshipFactory.reset_sequence(0)

    def test_unauthenticatedRequestReturn403(self):
        # log user1 out
        self.client.logout()

        response = self.client.post(self.url, {'id': self.user2.pk})
        self.assertEqual(response.status_code, 403)

    def test_unauthenticatedRequestReturnCorrentKeys(self):
        # log user1 out
        self.client.logout()

        response = self.client.post(self.url, {'id': self.user2.pk})
        data = json.loads(response.content)

        self.assertTrue('detail' in data.keys())

    def test_validRequestReturn204Success(self):
        response = self.client.post(self.url, {'id': self.user2.pk})
        self.assertEqual(response.status_code, 204)

    def test_validRequestReturnCorrectRelationship(self):
        response = self.client.post(self.url, {'id': self.user2.pk})

        # make sure no relationship record found for user1 and user2
        relationship_exist = UserRelationship.objects.filter(
            user1=self.user1, user2=self.user2).exists()
        self.assertTrue(not relationship_exist)

    def test_invalidRequestWithInvalidDataReturn400(self):
        response = self.client.post(self.url, {'id': INVALID_USER_PK})
        self.assertEqual(response.status_code, 400)

    def test_invalidRequestWithInvalidDataReturnCorrectKeys(self):
        response = self.client.post(self.url, {'id': INVALID_USER_PK})
        data = json.loads(response.content)
        self.assertTrue('detail' in data.keys())

    def test_invalidRequestWithNoDataReturn400(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 400)

    def test_invalidRequestWithNoDataReturnCorrectKeys(self):
        response = self.client.post(self.url)
        data = json.loads(response.content)
        self.assertTrue('detail' in data.keys())

    def test_invalidRequestWithWrongRelationTypeReturn400(self):
        # if user1 and user2 are not friends, then user1 shouldn't be able to
        # unfriend the non-existing friendship
        self.user_relationship.delete()

        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 400)

    def test_invalidRequestWithWrongRelationTypeReturnCorrectKeys(self):
        # if user1 and user2 are not friends, then user1 shouldn't be able to
        # unfriend the non-existing friendship
        self.user_relationship.delete()

        response = self.client.post(self.url)
        data = json.loads(response.content)
        self.assertTrue('detail' in data.keys())


class UserDetailTest(APITestCase):
    def setUp(self):
        super().setUp()
        self.user1 = AppUserFactory.create()
        self.good_url = reverse('user_detail', kwargs={
                                'username': self.user1.username})
        self.bad_url = reverse('user_detail', kwargs={
                               'username': 'BAD_USERNAME'})

    def tearDown(self):
        super().tearDown()
        AppUser.objects.all().delete()
        AppUserFactory.reset_sequence(0)

    def test_validRequestReturnSuccess(self):
        response = self.client.get(self.good_url)
        self.assertEqual(response.status_code, 200)

    def test_validRequestReturnCorrectResult(self):
        response = self.client.get(self.good_url)
        data = json.loads(response.content)

        self.assertEqual(data, {
            'id': self.user1.pk,
            'profile_image': TEST_SERVER_DOMAIN + self.user1.profile_image.url,
            'email': self.user1.email,
            'username': self.user1.username
        })

    def test_invalidRequestReturn404(self):
        response = self.client.get(self.bad_url)
        self.assertEqual(response.status_code, 404)

    def test_invalidRequestReturnCorrectKeys(self):
        response = self.client.get(self.bad_url)
        data = json.loads(response.content)

        self.assertTrue('detail' in data.keys())


class UserSearchListTest(APITestCase):
    def setUp(self):
        super().setUp()
        self.user1 = AppUserFactory.create(username='user1')
        self.user2 = AppUserFactory.create(username='user2')
        self.good_url = '{}?query={}'.format(reverse('user_search_list'), 'se')
        self.bad_url = '{}?query={}'.format(reverse('user_search_list'), '')

        # log user1 in
        self.client.login(email=self.user1.email, password=USER_PASSWORD)

    def tearDown(self):
        super().tearDown()
        AppUser.objects.all().delete()
        AppUserFactory.reset_sequence(0)

    def test_unauthenticatedRequestReturn403(self):
        # log user1 out
        self.client.logout()

        response = self.client.get(self.good_url)
        self.assertEqual(response.status_code, 403)

    def test_unauthenticatedRequestReturnCorrectKeys(self):
        # log user1 out
        self.client.logout()

        response = self.client.get(self.good_url)
        data = json.loads(response.content)
        self.assertTrue('detail' in data.keys())

    def test_validRequestReturnSuccess(self):
        response = self.client.get(self.good_url)
        self.assertEqual(response.status_code, 200)

    def test_validRequestReturnCorrectResult(self):
        response = self.client.get(self.good_url)
        data = json.loads(response.content)
        self.assertEqual(len(data), 2)
        self.assertEqual(data.sort(key=lambda x: x.get('id')), [{
            'id': self.user1.id,
            'profile_image': TEST_SERVER_DOMAIN + self.user1.profile_image.url,
            'email': self.user1.email,
            'username': self.user1.username
        }, {
            'id': self.user2.id,
            'profile_image': TEST_SERVER_DOMAIN + self.user2.profile_image.url,
            'email': self.user2.email,
            'username': self.user2.username
        }].sort(key=lambda x: x.get('id')))

    def test_invalidRequestReturn404(self):
        response = self.client.get(self.bad_url)

        self.assertEqual(response.status_code, 404)

    def test_invalidRequestReturnCorrectKeys(self):
        response = self.client.get(self.bad_url)
        data = json.loads(response.content)

        self.assertTrue('detail' in data.keys())


class FriendListTest(APITestCase):
    def setUp(self):
        super().setUp()
        self.user1 = AppUserFactory.create()
        self.user2 = AppUserFactory.create()
        # user1 and user2 are friends
        self.user_relationship = UserRelationshipFactory.create(
            user1=self.user1, user2=self.user2, relation_type='friends')

        self.good_url = reverse('friend_list_api', kwargs={
                                'username': self.user1.username})
        self.bad_url = reverse('friend_list_api', kwargs={
                               'username': 'NON_EXISTING_USERNAME'})

        # log user1 in
        self.client.login(email=self.user1.email, password=USER_PASSWORD)

    def tearDown(self):
        super().tearDown()
        AppUser.objects.all().delete()
        UserRelationship.objects.all().delete()
        AppUserFactory.reset_sequence(0)
        UserRelationshipFactory.reset_sequence(0)

    def test_unauthenticatedRequestReturn403(self):
        # log user1 out
        self.client.logout()

        response = self.client.get(self.good_url)
        self.assertEqual(response.status_code, 403)

    def test_unauthenticatedRequestReturnCorrectKeys(self):
        # log user1 out
        self.client.logout()

        response = self.client.get(self.good_url)
        data = json.loads(response.content)

        self.assertTrue('detail' in data.keys())

    def test_validRequestReturnSuccess(self):
        response = self.client.get(self.good_url)

        self.assertEqual(response.status_code, 200)

    def test_validRequestReturnCorrectResult(self):
        response = self.client.get(self.good_url)
        data = json.loads(response.content)

        self.assertEqual(len(data), 1)
        self.assertEqual(data, [{
            'id': self.user2.pk,
            'profile_image': TEST_SERVER_DOMAIN + self.user2.profile_image.url,
            'username': self.user2.username
        }])

    def test_invalidUsernameReturn404(self):
        response = self.client.get(self.bad_url)

        self.assertEqual(response.status_code, 404)

    def test_invalidUsernameReturnCorrectKeys(self):
        response = self.client.get(self.bad_url)
        data = json.loads(response.content)

        self.assertTrue('detail' in data.keys())
