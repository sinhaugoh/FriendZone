from django.test import TestCase

from ..forms import *
from ..model_factories import *


class RegistrationFormTest(TestCase):
    def setUp(self):
        super().setUp()
        self.user1 = AppUserFactory.create()
        self.input = {
            'username': 'Valid_username',
            'email': 'Test@Email.com',
            'password1': 'VBAEdafd123',
            'password2': 'VBAEdafd123',
        }

    def tearDown(self):
        super().tearDown()
        AppUser.objects.all().delete()
        AppUserFactory.reset_sequence(0)

    def test_registrationFormContainRequiredFields(self):
        form = RegistrationForm()

        self.assertIn('email', form.fields)
        self.assertIn('username', form.fields)
        self.assertIn('password1', form.fields)
        self.assertIn('password2', form.fields)

    def test_registrationFormWithValidInputReturnValid(self):
        form = RegistrationForm(data=self.input)

        self.assertTrue(form.is_valid())

    def test_registrationFormWithExistingEmailReturnInvalid(self):
        self.input['email'] = self.user1.email
        form = RegistrationForm(data=self.input)

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['email'], ['Email already in use.'])

    def test_registrationFormWithExistingUsernameReturnInvalid(self):
        self.input['username'] = self.user1.username
        form = RegistrationForm(data=self.input)

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['username'], ['Username already in use.'])

    def test_registrationFormReturnLowercaseEmail(self):
        form = RegistrationForm(data=self.input)

        self.assertTrue(form.is_valid())
        self.assertEqual(
            form.cleaned_data['email'], self.input['email'].lower())

    def test_registrationFormReturnLowercaseUsername(self):
        form = RegistrationForm(data=self.input)

        self.assertTrue(form.is_valid())
        self.assertEqual(
            form.cleaned_data['username'], self.input['username'].lower())


class LoginFormTest(TestCase):
    def setUp(self):
        super().setUp()
        self.user1 = AppUserFactory.create()
        self.user1_password = 'Asdf1234'

    def tearDown(self):
        super().tearDown()
        AppUser.objects.all().delete()
        AppUserFactory.reset_sequence(0)

    def test_loginFormContainRequiredFields(self):
        form = LoginForm()

        self.assertIn('email', form.fields)
        self.assertIn('password', form.fields)

    def test_loginFormWithValidInputReturnValid(self):
        form = LoginForm(data={'email': self.user1.email,
                         'password': self.user1_password})

        self.assertTrue(form.is_valid())

    def test_loginFormWithInvalidEmailReturnInvalid(self):
        form = LoginForm(
            data={'email': 'invalid@email.com', 'password': self.user1_password})

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['__all__'], [
                         'Incorrect email or password. Please try again'])

    def test_loginFormWithInvalidPasswordReturnInvalid(self):
        form = LoginForm(data={'email': self.user1.email,
                         'password': 'INVALID_PASSWORD123'})

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['__all__'], [
                         'Incorrect email or password. Please try again'])

    def test_registrationFormWithUppercaseEmailReturnValid(self):
        form = LoginForm(
            data={'email': self.user1.email.upper(), 'password': self.user1_password})

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['email'], self.user1.email)


class ProfileUpdateFormTest(TestCase):
    def setUp(self):
        super().setUp()
        self.user1 = AppUserFactory.create()
        self.user2 = AppUserFactory.create()

    def tearDown(self):
        super().tearDown()
        AppUser.objects.all().delete()
        AppUserFactory.reset_sequence(0)

    def test_profileUpdateFormContainRequiredFields(self):
        form = ProfileUpdateForm()

        self.assertIn('profile_image', form.fields)
        self.assertIn('email', form.fields)
        self.assertIn('username', form.fields)

    def test_profileUpdateFormWithValidInputReturnValid(self):
        form = ProfileUpdateForm(data={'username': 'new_username',
                                       'email': 'new_email@email.com',
                                       }, instance=self.user1)

        self.assertTrue(form.is_valid())

    def test_profileUpdateFormWithExistingEmailReturnInvalid(self):
        form = ProfileUpdateForm(
            data={'email': self.user2.email}, instance=self.user1)

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['email'], ['Email already in use.'])

    def test_profileUpdateFormWithExistingUsernameReturnInvalid(self):
        form = ProfileUpdateForm(
            data={'username': self.user2.username}, instance=self.user1)

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['username'], ['Username already in use.'])

    def test_profileUpdateFormReturnLowercaseEmail(self):
        email_input = 'VALID@EMAIL.COM'
        form = ProfileUpdateForm(
            data={'email': email_input, 'username': self.user1.username}, instance=self.user1)

        self.assertTrue(form.is_valid())
        self.assertEqual(
            form.cleaned_data['email'], email_input.lower())

    def test_profileUpdateFormReturnLowercaseUsername(self):
        username_input = 'VALIDUSERNAME'
        form = ProfileUpdateForm(
            data={'email': self.user1.email, 'username': username_input}, instance=self.user1)

        self.assertTrue(form.is_valid())
        self.assertEqual(
            form.cleaned_data['username'], username_input.lower())


class PostFormTest(TestCase):
    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_postFormContainRequiredFields(self):
        form = PostForm()

        self.assertIn('text', form.fields)
        self.assertIn('image', form.fields)

    def test_postFormWithValidInputReturnValid(self):
        form = PostForm(data={'text': 'TEST'})

        self.assertTrue(form.is_valid())

    def test_postFormWithNoTextAndImageReturnInvalid(self):
        form = PostForm(data={})

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['__all__'], [
                         'You must at least provide an image or status text'])
