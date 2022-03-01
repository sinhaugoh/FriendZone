import factory

from .models import *

class AppUserFactory(factory.django.DjangoModelFactory):
    email = factory.Sequence(lambda n: 'user{}@email.com'.format(n))
    username = factory.Sequence(lambda n: 'user{}'.format(n))
    password = factory.PostGenerationMethodCall('set_password', 'Asdf1234')


    class Meta:
        model = AppUser
        

class UserRelationshipFactory(factory.django.DjangoModelFactory):
    user1 = factory.SubFactory(AppUserFactory)
    user2 = factory.SubFactory(AppUserFactory)
    
    class Meta:
        model = UserRelationship
        

class PostFactory(factory.django.DjangoModelFactory):
    text = 'This is a status update text'
    owner = factory.SubFactory(AppUserFactory)
    image = factory.django.ImageField()
    
    class Meta:
        model = Post