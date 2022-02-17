from unicodedata import name
from django.urls import path
from .views import index, register, user_login, user_logout, profile, search_user, update_profile

urlpatterns = [
    path('', index, name='index'),
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('profile/<int:id>', profile, name='profile'),
    path('search/', search_user, name='search'),
    path('profile/update/', update_profile, name='update_profile'),
]
