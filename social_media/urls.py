from unicodedata import name
from django.urls import path
from django.contrib.auth.views import PasswordChangeView
from .views import index, register, user_login, user_logout, profile, search_user, profile_update, password_change

urlpatterns = [
    path('', index, name='index'),
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('profile/<int:id>', profile, name='profile'),
    path('search/', search_user, name='search'),
    path('password_change/', password_change, name='password_change'),
    path('profile/update/', profile_update, name='profile_update'),
]
