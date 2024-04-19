from django.urls import path
from django.contrib.auth.views import LoginView
from django.contrib.auth.views import LogoutView
from . import views
from .views import create_video,update_video,delete_video
from .views import video_feed

urlpatterns = [
    path('', views.home),
    path('register', views.register,name="register"),
    path('home',views.home,name="home"),
    # path('login/', LoginView.as_view(), name='login'),
    # path('logout/', LogoutView.as_view(), name='logout'),
    path('create_video', views.create_video),
    path('update_video', views.update_video),
    path('delete_video', views.delete_video, name='delete_video'),
    #path('videos/>', views.video_feed, name='video_stream'),
    path('videos', views.video_feed, name='video_stream')

    
    
]




