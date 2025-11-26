from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('api/users', views.get_users, name='get_users'),
    path('api/auth/start', views.start_auth, name='start_auth'),
    path('auth/callback', views.auth_callback, name='auth_callback'),
    path('api/users/<str:email>/', views.delete_user, name='delete_user'),
    path('api/health', views.health, name='health'),
]

