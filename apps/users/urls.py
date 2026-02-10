from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_user, name='login'),
    path('add_user/', views.add_user, name='add_user'),
]