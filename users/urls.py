from django.conf.urls import url, include
from django.contrib import admin
from .views import RegisterView, LoginView, LogoutView, ActiveView, ChangePasswordView

app_name = 'users'

urlpatterns = [
    url('register/', RegisterView.as_view(), name='register'),
    url('login/', LoginView.as_view(), name="login"),
    url('logout/', LogoutView.as_view(), name="logout"),
    url('active/', ActiveView.as_view(), name="active"),
    url('change_password/', ChangePasswordView.as_view(), name="change_password"),
]
