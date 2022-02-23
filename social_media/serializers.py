from rest_framework import serializers

from .models import Post, AppUser

class AppUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppUser
        fields = [
            'profile_image',
            'email',
            'username'
        ]

class PostSerializer(serializers.ModelSerializer):
    # owner = AppUserSerializer()
    
    class Meta:
        model = Post
        fields = [
            # 'owner',
            'image',
            'text',
            'date_created'   
        ]