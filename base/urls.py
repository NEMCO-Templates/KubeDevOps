from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.loginPage, name="login"),
    path("logout/", views.logoutUser, name="logout"),
    path("register/", views.registerPage, name="registerPage"),
    path("", views.home, name="home"),
    path("room_page/<str:pk>", views.room, name="room"),
    path("profile/<str:pk>", views.userProfile, name="user-profile"),
    path("create-room/", views.createRoom, name="create-room"),
    path("update-room/<str:pk>/", views.updateRoom, name="update-room"),
    path("delete-room/<str:pk>/", views.deleteRoom, name="delete-room"),
    path("delete-message/<str:pk>/", views.deleteMessage, name="delete-message"),
    path("update-user/", views.updateUser, name="update-user"),
    path("topic/", views.topicsPage, name="topic"),
    path("activity/", views.activityPage, name="activity"),
    path('follow_user/<str:userId>/', views.follow_user, name='follow_user'),
    path('unfollow_user/<str:userId>/', views.unfollow_user, name='unfollow_user'),
    path('delete_notification/<str:pk>/', views.delete_notification, name='delete_notification'),
    path('game/', views.gamePage, name='game'),
    path('startGame/<str:pk>', views.startGame, name='startGame'),
    path('game_view/<str:game_id>', views.game_view, name='game_view'),
    path('send', views.send, name='send'),
    path('getMessages/<str:pk>/', views.getMessages, name='getMessages'),
    
    #######################################################################################
    path('up_vote/<str:pk>', views.up_vote_room, name='up_vote'),
    path('down_vote/<str:pk>', views.down_vote_room, name='down_vote'),
    #######################################################################################
]