from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('add_user/', views.add_user, name='add_user'),
    path('users', views.users_list, name='users_list'),
    path('user/<int:id>', views.user_detail, name='user'),
]