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
                    friend_requests_list,)

from .apis import (FriendList, SendFriendRequest, UserSearchList, CancelFriendRequest,
                   AcceptFriendRequest,
                   DeclineFriendRequest,
                   RemoveFriend,
                   CreatePost,
                   UserPostList, UserDetail)

urlpatterns = [
    # views
    path('', index, name='index'),
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('search/', search_user, name='search'),
    path('user/<str:username>/', profile, name='profile'),
    path('user/<str:username>/friends/', friend_list, name='friend_list'),
    path('account/password_change/', password_change, name='password_change'),
    path('account/update/', profile_update, name='profile_update'),
    path('account/friend_requests/', friend_requests_list, name='friend_requests'),

    # apis
    path('api/friend_request/', SendFriendRequest.as_view(), name='send_friend_request'),
    path('api/friend_request_cancel', CancelFriendRequest.as_view(),
         name='cancel_friend_request'),
    path('api/friend_request_accept/', AcceptFriendRequest.as_view(),
         name='accept_friend_request'),
    path('api/friend_request_decline/', DeclineFriendRequest.as_view(),
         name='decline_friend_request'),
    path('api/friend_remove/', RemoveFriend.as_view() , name='remove_friend'),
#     path('api/post/create/', create_post, name='create_post'),
    path('api/post/create/', CreatePost.as_view(), name='create_post'),
    path('api/user/<str:username>/posts/', UserPostList.as_view(), name='user_posts'),
    
    ###### NOT USED #########
    path('api/user/<str:username>/friends/', FriendList.as_view(), name='friend_list_api'),
    path('api/user/<str:username>/', UserDetail.as_view(), name='user_detail'),
    path('api/user/search', UserSearchList.as_view(), name='user_search_list'),
]
