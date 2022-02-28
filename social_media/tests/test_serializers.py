from django.test import TestCase, override_settings
import tempfile
import shutil


from ..models import AppUser, Post
from ..model_factories import AppUserFactory, PostFactory
from ..serializers import AppUserSerializer, FriendListSerializer, PostSerializer

MEDIA_ROOT = tempfile.mkdtemp()


class AppUserSerializerTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user1 = AppUserFactory.create()
        cls.serializer = AppUserSerializer(instance=cls.user1)
        cls.serializer_data = cls.serializer.data

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        AppUser.objects.all().delete()
        AppUserFactory.reset_sequence(0)

    def test_appUserSerializerHasCorrectKeys(self):
        self.assertEqual(set(self.serializer_data.keys()), set([
            'id',
            'profile_image',
            'username',
            'email'
        ]))

    def test_idHasCorrectValue(self):
        self.assertEqual(self.serializer_data['id'], self.user1.pk)

    def test_profileImageHasCorrectValue(self):
        self.assertEqual(
            self.serializer_data['profile_image'], self.user1.profile_image.url)

    def test_usernameHasCorrectValue(self):
        self.assertEqual(self.serializer_data['username'], self.user1.username)

    def test_emailHasCorrectValue(self):
        self.assertEqual(self.serializer_data['email'], self.user1.email)


class FriendListSerializerTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user1 = AppUserFactory.create()
        cls.serializer = FriendListSerializer(instance=cls.user1)
        cls.serializer_data = cls.serializer.data

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        AppUser.objects.all().delete()
        AppUserFactory.reset_sequence(0)

    def test_friendListSerializerHasCorrectKeys(self):
        self.assertEqual(set(self.serializer_data.keys()), set([
            'id',
            'profile_image',
            'username',
        ]))

    def test_idHasCorrectValue(self):
        self.assertEqual(self.serializer_data['id'], self.user1.pk)

    def test_profileImageHasCorrectValue(self):
        self.assertEqual(
            self.serializer_data['profile_image'], self.user1.profile_image.url)

    def test_usernameHasCorrectValue(self):
        self.assertEqual(self.serializer_data['username'], self.user1.username)


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class PostSerializerTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user1 = AppUserFactory.create()
        cls.post1 = PostFactory.create(owner=cls.user1)
        cls.serializer = PostSerializer(instance=cls.post1)
        cls.serializer_data = cls.serializer.data

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        AppUser.objects.all().delete()
        AppUserFactory.reset_sequence(0)
        Post.objects.all().delete()
        PostFactory.reset_sequence(0)

        # remove test image temp folder
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)

    def test_postSerializerHasCorrectKeys(self):
        self.assertEqual(set(self.serializer_data.keys()), set([
            'image',
            'text',
            'date_created',
        ]))

    def test_imageHasCorrectValue(self):
        self.assertEqual(self.serializer_data['image'], self.post1.image.url)

    def test_textHasCorrectValue(self):
        self.assertEqual(self.serializer_data['text'], self.post1.text)

    def test_dateCreatedHasCorrectValue(self):
        formatted_date = self.post1.date_created.strftime(
            "%Y-%m-%dT%H:%M:%S.%fZ")
        self.assertEqual(self.serializer_data['date_created'], formatted_date)
