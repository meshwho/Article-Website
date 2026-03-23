from django.urls import path
from .views import custom_logout, dashboard, home, register

urlpatterns = [
    path('', home, name='home'),
    path('register/', register, name='register'),
    path('dashboard/', dashboard, name='dashboard'),
    path('logout/', custom_logout, name='custom_logout'),
]