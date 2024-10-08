from django.urls import path
from django.contrib.auth import views as auth_views
from . import views  # This imports your app's views.py

urlpatterns = [
    path('', views.home, name='home'),  # Existing home view
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),  # Restricted page
]
