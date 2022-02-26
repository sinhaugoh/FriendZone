from django.forms import ImageField
from rest_framework import serializers

from .models import Post, AppUser

class AppUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppUser
        fields = [
            'id',
            'profile_image',
            'email',
            'username'
        ]
        
class FriendListSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppUser
        fields = [
            'id',
            'profile_image',
            'username'
        ]

class PostSerializer(serializers.ModelSerializer):
    image = ImageField(max_length=256, allow_empty_file=True)
    
    class Meta:
        model = Post
        fields = [
            # 'owner',
            'image',
            'text',
            'date_created'   
        ]
        
    # def create(self, validated_data):
    #     print('create')
    #     image = validated_data['image']
    #     text = validated_data['text']
    #     # make sure at least one of them is provided
    #     if image is None and text is None:
    #         raise serializers.ValidationError('You must at least provide an image or status text.')
        
    #     return Post.objects.create(**validated_data)