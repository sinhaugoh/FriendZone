from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.forms import ValidationError
from .storage import OverwriteFileStorage

DEFAULT_PROFILE_IMAGE_PATH = 'images/default_images/default_profile.png'

# retrieve profile image path
def get_profile_image_path(instance, _):
    return 'images/profile_images/{}/profile_image.jpg'.format(str(instance.pk))

def get_post_image_path(instance, _):
    return 'images/post_images/{}/{}/post_image.jpg'.format(str(instance.owner.pk),str(instance.pk))


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
                                      upload_to=get_profile_image_path, storage=OverwriteFileStorage(), default=DEFAULT_PROFILE_IMAGE_PATH)

    # set email field as username
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = AppUserManager()
    
    
RELATION_TYPE = (
    ('pending_user1_user2', 'pending_user1_user2'),
    ('pending_user2_user1','pending_user2_user1'),
    ('friends', 'friends'),
)
class UserRelationship(models.Model):
    # user1 id is always smaller than user2 id
    user1 = models.ForeignKey(AppUser, on_delete=models.CASCADE, related_name='user1')
    user2 = models.ForeignKey(AppUser, on_delete=models.CASCADE, related_name='user2')
    relation_type = models.CharField(max_length=50, choices=RELATION_TYPE, blank=False, null=False)
    date_modified = models.DateTimeField( auto_now=True)

    class Meta:
        unique_together = ('user1', 'user2')
        
    def __str__(self):
        return '{} -- {}  type: {}'.format(self.user1.username, self.user2.username, self.relation_type)

    def accept_friend_request(self):
        self.relation_type = 'friends'
        self.save()
        
     
class Post(models.Model):
    image = models.ImageField(max_length=256, blank=True, null=True, upload_to=get_post_image_path)
    text = models.CharField(max_length=500,blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    
    # class Meta:
    #     constraints = [
    #         models.CheckConstraint(
    #             # database check
    #             check=models.Q(image=None, text__isnull=False) |
    #                   models.Q(text=None, image__isnull=False),
    #             name='Image or text should not be empty.'
    #         )
    #     ]
    
    def clean(self, *args, **kwargs):
        # make sure at least image or text must exist
        if self.image is None and self.text is None:
            raise ValidationError('Image or text should not be empty.')
        
        return super().clean(*args, **kwargs)