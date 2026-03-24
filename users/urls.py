from django.urls import path
from .views import custom_logout, dashboard, home, profile, register

urlpatterns = [
    path('', home, name='home'),
    path('register/', register, name='register'),
    path('dashboard/', dashboard, name='dashboard'),
    path('profile/', profile, name='profile'),
    path('logout/', custom_logout, name='custom_logout'),
]