from django.conf.urls import include
from django.urls import path
from rest_framework import routers

from . import views


class Router(routers.DefaultRouter):
    pass


urlpatterns = [
    path('login/', views.LoginView.as_view()),
    path('logout/', views.LogoutView.as_view()),
    path('whoami/', views.WhoAmIView.as_view()),
    path('password-reset/', include('django_rest_passwordreset.urls', namespace='password_reset')),
    path('password-change/', views.PasswordChangeView.as_view()),
]
