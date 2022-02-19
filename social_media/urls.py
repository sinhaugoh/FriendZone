from django.urls import path
from .views import (index, 
                    register, 
                    user_login, 
                    user_logout, 
                    profile, 
                    search_user, 
                    profile_update, 
                    password_change,
                    friend_list,
                    friend_requests_list,
                    )

from .apis import send_friend_request, cancel_friend_request

urlpatterns = [
    # views
    path('', index, name='index'),
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('search/', search_user, name='search'),
    path('password_change/', password_change, name='password_change'),
    path('profile/<int:id>/', profile, name='profile'),
    path('profile/<int:id>/friends/', friend_list, name='friend_list'),
    path('profile/update/', profile_update, name='profile_update'),
    path('profile/friend_requests/', friend_requests_list, name='friend_requests'),
    
    # apis
    path('api/friend_request/', send_friend_request, name='send_friend_request'),
    path('api/friend_request_cancel', cancel_friend_request, name='cancel_friend_request'),
]
