from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import AppUser, UserRelationship, Post

# add new section to the interface
UserAdmin.fieldsets += ('other fields', {'fields': ('profile_image',)}),

admin.site.register(AppUser, UserAdmin)
admin.site.register(UserRelationship)
admin.site.register(Post)