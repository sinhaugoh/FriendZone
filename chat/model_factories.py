import factory

from .models import *
from social_media.model_factories import *


class MessageFactory(factory.django.DjangoModelFactory):
    content = 'TEXT MESSAGE'
    receiver = factory.SubFactory(AppUserFactory)
    sender = factory.SubFactory(AppUserFactory)

    class Meta:
        model = AppUser
