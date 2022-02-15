from pyexpat import model
from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser

DEFAULT_PROFILE_IMAGE_PATH = 'default_images/default_profile.png'

def get_profile_image_path(instance, filename):
    return 'profile_images/{}/{}'.format(str(instance.pk), filename)


class AppUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **other_fields):
        if not email:
            raise ValueError('Email must not be empty.')

        if not password:
            raise ValueError('Password must not be empty')

        # normalise the email input
        email = self.normalize_email(email)
        new_user = self.model(email=email, username=username, **other_fields)
        new_user.set_password(password)
        new_user.save()

        return new_user

    def create_superuser(self, email, username, password=None, **other_fields):
        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)
        other_fields.setdefault('is_active', True)

        if not other_fields.get('is_staff'):
            raise ValueError('is_staff field must set to True')
        if not other_fields.get('is_superuser'):
            raise ValueError('is_superuser must set to True')

        # normalise the email input
        email = self.normalize_email(email)
        new_superuser = self.create_user(
            email=email, username=username, password=password, **other_fields)
        new_superuser.save()

        return new_superuser


class AppUser(AbstractUser):
    email = models.EmailField(
        max_length=256, null=False, blank=False, unique=True)
    profile_image = models.ImageField(max_length=256, null=True, blank=True,
                                      upload_to=get_profile_image_path, default=DEFAULT_PROFILE_IMAGE_PATH)

    # set email field as username
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = AppUserManager()
    