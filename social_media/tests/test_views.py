from django.test import TestCase, override_settings
from django.urls import reverse
import tempfile
import shutil

from ..model_factories import *

USER_PASSWORD = 'Asdf1234'
MEDIA_ROOT = tempfile.mkdtemp()
TEST_SERVER_DOMAIN = 'http://testserver'


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class IndexViewTest(TestCase):
    def setUp(self):
        super().setUp()
        self.user1 = AppUserFactory.create()
        self.user2 = AppUserFactory.create()

        # make user1 and user2 friends
        UserRelationshipFactory.create(
            user1=self.user1, user2=self.user2, relation_type='friends')

        # create a post from user2
        self.post1 = PostFactory.create(owner=self.user2)

        self.url = reverse('index')

        # log user1 in
        self.client.login(email=self.user1.email, password=USER_PASSWORD)

    def tearDown(self):
        super().setUp()
        AppUser.objects.all().delete()
        UserRelationship.objects.all().delete()
        Post.objects.all().delete()
        AppUserFactory.reset_sequence(0)
        UserRelationshipFactory.reset_sequence(0)
        PostFactory.reset_sequence(0)

        # remove test image temp folder
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)

    def test_redirectIfNotLoggedIn(self):
        # log user1 out
        self.client.logout()

        response = self.client.get(self.url)
        self.assertRedirects(response, '/login/?next=/')

    def test_urlIsWorking(self):
        response = self.client.get('/')

        self.assertEqual(response.status_code, 200)

    def test_urlByNameIsWorking(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

    def test_loggedInUsesCorrectTemplate(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'social_media/index.html')

    def test_loggedInReturnCorrectPosts(self):
        response = self.client.get(self.url)

        self.assertEqual(len(response.context['posts']), 1)
        self.assertEqual(response.context['posts'], [{
            'owner_username': self.post1.owner.username,
            'owner_profile_image_path': self.post1.owner.profile_image.url,
            'post_text': self.post1.text,
            'post_image_path': self.post1.image.url,
            'post_date_created': self.post1.date_created
        }])


class UserLoginViewTest(TestCase):
    def setUp(self):
        super().setUp()
        self.user1 = AppUserFactory.create()

        self.url = reverse('login')

    def tearDown(self):
        super().tearDown()
        AppUser.objects.all().delete()
        AppUserFactory.reset_sequence(0)

    def test_urlIsWorking(self):
        response = self.client.get('/login/')

        self.assertEqual(response.status_code, 200)

    def test_urlByNameIsWorking(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

    def test_redirectIfAuthenticated(self):
        # log user1 in
        self.client.login(email=self.user1, password=USER_PASSWORD)

        response = self.client.get(self.url)

        self.assertRedirects(response, '/')

    def test_loggedInUsesCorrectTemplate(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'social_media/login.html')

    def test_redirectToIndexOnSuccess(self):
        response = self.client.post(
            self.url, {'email': self.user1.email, 'password': USER_PASSWORD})

        self.assertRedirects(response, '/')

    def test_formInvalidEmail(self):
        response = self.client.post(
            self.url, {'email': 'INVALID@EMAIL.COM', 'password': USER_PASSWORD})

        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'login_form', '__all__',
                             'Incorrect email or password. Please try again')

    def test_formInvalidPassword(self):
        response = self.client.post(
            self.url, {'email': self.user1.email, 'password': 'INVALID_PASSSWORD123'})

        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'login_form', '__all__',
                             'Incorrect email or password. Please try again')


class RegisterViewTest(TestCase):
    def setUp(self):
        super().setUp()

        self.user1 = AppUserFactory.create()
        self.input = {
            'email': 'VALID@EMAIL.COM',
            'username': 'VALID',
            'password1': 'Fdafda213',
            'password2': 'Fdafda213'
        }

        self.url = reverse('register')

    def tearDown(self):
        super().tearDown()
        AppUser.objects.all().delete()
        AppUserFactory.reset_sequence(0)

    def test_urlIsWorking(self):
        response = self.client.get('/register/')

        self.assertEqual(response.status_code, 200)

    def test_urlByNameIsWorking(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

    def test_redirectIfAuthenticated(self):
        # log user1 in
        self.client.login(email=self.user1, password=USER_PASSWORD)

        response = self.client.get(self.url)

        self.assertRedirects(response, '/')

    def test_loggedInUsesCorrectTemplate(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, 'social_media/user_registration.html')

    def test_redirectToIndexOnSuccess(self):
        response = self.client.post(self.url, self.input)

        self.assertRedirects(response, '/')

    def test_formInvalidEmail(self):
        self.input['email'] = self.user1.email

        response = self.client.post(self.url, self.input)

        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'registration_form',
                             'email', 'Email already in use.')

    def test_formInvalidUsername(self):
        self.input['username'] = self.user1.username

        response = self.client.post(self.url, self.input)

        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'registration_form',
                             'username', 'Username already in use.')


class PasswordChangeViewTest(TestCase):
    def setUp(self):
        super().setUp()
        self.user1 = AppUserFactory.create()
        self.url = reverse('password_change')
        self.input = {
            'old_password': USER_PASSWORD,
            'new_password1': 'VALID_PW123',
            'new_password2': 'VALID_PW123'
        }

        # log user1 in
        self.client.login(email=self.user1.email, password=USER_PASSWORD)

    def tearDown(self):
        super().tearDown()
        AppUser.objects.all().delete()
        AppUserFactory.reset_sequence(0)

    def test_urlIsWorking(self):
        response = self.client.get('/account/password_change/')

        self.assertEqual(response.status_code, 200)

    def test_urlByNameIsWorking(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

    def test_redirectIfNotAuthenticated(self):
        # log user1 out
        self.client.logout()

        response = self.client.get(self.url)

        self.assertRedirects(
            response, '/login/?next=/account/password_change/')

    def test_loggedInUsesCorrectTemplate(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'social_media/change_password.html')

    def test_redirectToIndexOnSuccess(self):
        response = self.client.post(self.url, self.input)

        self.assertRedirects(response, '/')


class LogoutViewTest(TestCase):
    def setUp(self):
        super().setUp()
        self.user1 = AppUserFactory.create()
        self.url = reverse('logout')

        # log user1 in
        self.client.login(email=self.user1.email, password=USER_PASSWORD)

    def tearDown(self):
        super().tearDown()
        AppUser.objects.all().delete()
        AppUserFactory.reset_sequence(0)

    def test_redirectIfNotAuthenticated(self):
        # log user1 out
        self.client.logout()

        response = self.client.get(self.url)

        self.assertRedirects(response, '/login/?next=/logout/')

    def test_redirectToLoginOnSuccess(self):
        response = self.client.get(self.url)

        self.assertRedirects(response, '/login/')


class ProfileViewTest(TestCase):
    def setUp(self):
        super().setUp()
        self.user1 = AppUserFactory.create()
        self.user2 = AppUserFactory.create()
        self.url = reverse('profile', kwargs={'username': self.user2.username})

    def tearDown(self):
        super().tearDown()
        AppUser.objects.all().delete()
        AppUserFactory.reset_sequence(0)

    def test_urlIsWorking(self):
        response = self.client.get('/user/{}/'.format(self.user2.username))

        self.assertEqual(response.status_code, 200)

    def test_urlByNameIsWorking(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

    def test_usesCorrectTemplate(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'social_media/profile.html')

    def test_invalidRequestReturn404(self):
        response = self.client.get(
            reverse('profile', kwargs={'username': 'INVALID_USERNAME'}))

        self.assertEqual(response.status_code, 404)

    def test_validRequestReturnCorrectContext(self):
        response = self.client.get(self.url)

        self.assertEqual(response.context['id'], self.user2.pk)
        self.assertEqual(response.context['username'], self.user2.username)
        self.assertEqual(response.context['email'], self.user2.email)
        self.assertEqual(
            response.context['profile_image_url'], self.user2.profile_image.url)
        self.assertEqual(response.context['is_own_profile'], False)
        self.assertEqual(response.context['is_authenticated'], False)


class SearchUserViewTest(TestCase):
    def setUp(self):
        super().setUp()
        # create 7 users
        AppUserFactory.create_batch(7)
        self.url = reverse('search')

        # log user1 in
        self.client.login(email='user1@email.com', password=USER_PASSWORD)

    def tearDown(self):
        super().tearDown()
        AppUser.objects.all().delete()
        AppUserFactory.reset_sequence(0)

    def test_urlIsWorking(self):
        response = self.client.get('/search/?query={}'.format('user'))

        self.assertEqual(response.status_code, 200)

    def test_urlByNameIsWorking(self):
        response = self.client.get(self.url + '?query=user')

        self.assertEqual(response.status_code, 200)

    def test_redirectIfNotAuthenticated(self):
        # log user1 out
        self.client.logout()

        response = self.client.get(self.url)

        self.assertRedirects(response, '/login/?next=/search/')

    def test_loggedInUsesCorrectTemplate(self):
        response = self.client.get(self.url + '?query=user')

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'social_media/search_result.html')

    def test_invalidParamReturn404(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 404)

    def test_paginationIs5(self):
        response = self.client.get(self.url + '?query=user')

        self.assertEqual(response.status_code, 200)
        self.assertTrue('paginated_results' in response.context)
        self.assertEqual(len(response.context['paginated_results']), 5)

    def test_paginationLastPageLength(self):
        response = self.client.get(self.url + '?query=user&page=2')

        self.assertEqual(response.status_code, 200)
        self.assertTrue('paginated_results' in response.context)
        # 7 users - self - 5 = 1 left
        self.assertEqual(len(response.context['paginated_results']), 1)


class ProfileUpdateViewTest(TestCase):
    def setUp(self):
        super().setUp()
        self.user1 = AppUserFactory.create()
        self.user2 = AppUserFactory.create()
        self.url = reverse('profile_update')
        self.input = {
            'email': 'valid@email.com',
            'username': 'valid_username',
        }

        # log user1 in
        self.client.login(email=self.user1.email, password=USER_PASSWORD)

    def tearDown(self):
        super().tearDown()
        AppUser.objects.all().delete()
        AppUserFactory.reset_sequence(0)

    def test_urlIsWorking(self):
        response = self.client.get('/account/update/')

        self.assertEqual(response.status_code, 200)

    def test_urlByNameIsWorking(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

    def test_redirectIfNotAuthenticated(self):
        # log user1 out
        self.client.logout()

        response = self.client.get(self.url)

        self.assertRedirects(response, '/login/?next=/account/update/')

    def test_loggedInUsesCorrectTemplate(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'social_media/update_profile.html')

    def test_redirectToIndexOnSuccess(self):
        response = self.client.post(self.url, self.input)

        self.assertRedirects(response, '/user/valid_username/')

    def test_formInitialValueCorrect(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context['profile_update_form'].initial['email'], self.user1.email)
        self.assertEqual(
            response.context['profile_update_form'].initial['username'], self.user1.username)
        self.assertEqual(
            response.context['profile_update_form'].initial['profile_image'], self.user1.profile_image)

    def test_formInvalidEmail(self):
        self.input['email'] = self.user2.email

        response = self.client.post(self.url, self.input)

        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'profile_update_form',
                             'email', 'Email already in use.')

    def test_formInvalidUsername(self):
        self.input['username'] = self.user2.username

        response = self.client.post(self.url, self.input)

        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'profile_update_form',
                             'username', 'Username already in use.')


class FriendListViewTest(TestCase):
    def setUp(self):
        super().setUp()
        self.user1 = AppUserFactory.create()
        self.user2 = AppUserFactory.create()
        self.url = reverse('friend_list', kwargs={
                           'username': self.user1.username})

        # make user1 and user2 friend
        UserRelationshipFactory.create(
            user1=self.user1, user2=self.user2, relation_type='friends')

        # log user1 in
        self.client.login(email=self.user1.email, password=USER_PASSWORD)

    def tearDown(self):
        super().tearDown()
        AppUser.objects.all().delete()
        UserRelationship.objects.all().delete()
        AppUserFactory.reset_sequence(0)
        UserRelationshipFactory.reset_sequence(0)

    def test_urlIsWorking(self):
        response = self.client.get(
            '/user/{}/friends/'.format(self.user1.username))

        self.assertEqual(response.status_code, 200)

    def test_urlByNameIsWorking(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

    def test_redirectIfNotAuthenticated(self):
        # log user1 out
        self.client.logout()

        response = self.client.get(self.url)

        self.assertRedirects(
            response, '/login/?next=/user/{}/friends/'.format(self.user1.username))

    def test_loggedInUsesCorrectTemplate(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'social_media/friend_list.html')

    def test_invalidUsernameReturn404(self):
        response = self.client.get(
            reverse('friend_list', kwargs={'username': 'INVALID_USERNAME'}))

        self.assertEqual(response.status_code, 404)

    def test_validRequestReturnCorrectResult(self):
        response = self.client.get(self.url)

        self.assertEqual(response.context['friends'], [{
            'id': self.user2.pk,
            'profile_image_url': self.user2.profile_image.url,
            'username': self.user2.username,
        }])


class FriendRequestsListViewTest(TestCase):
    def setUp(self):
        super().setUp()
        self.user1 = AppUserFactory.create()
        self.user2 = AppUserFactory.create()
        self.url = reverse('friend_requests')

        # user2 sends user1 friend request
        UserRelationshipFactory.create(
            user1=self.user1, user2=self.user2, relation_type='pending_user2_user1')

        # log user1 in
        self.client.login(email=self.user1.email, password=USER_PASSWORD)

    def tearDown(self):
        super().tearDown()
        AppUser.objects.all().delete()
        UserRelationship.objects.all().delete()
        AppUserFactory.reset_sequence(0)
        UserRelationshipFactory.reset_sequence(0)

    def test_urlIsWorking(self):
        response = self.client.get('/account/friend_requests/')

        self.assertEqual(response.status_code, 200)

    def test_urlByNameIsWorking(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

    def test_redirectIfNotAuthenticated(self):
        # log user1 out
        self.client.logout()

        response = self.client.get(self.url)

        self.assertRedirects(
            response, '/login/?next=/account/friend_requests/')

    def test_loggedInUsesCorrectTemplate(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, 'social_media/friend_request_list.html')

    def test_validRequestReturnCorrectResult(self):
        response = self.client.get(self.url)

        self.assertEqual(response.context['friend_requests'], [{
            'id': self.user2.pk,
            'profile_image_url': self.user2.profile_image.url,
            'username': self.user2.username,
        }])
