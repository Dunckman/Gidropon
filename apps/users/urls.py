from django.urls import path
from . import views

urlpatterns = [
    path('', views.start, name='start'),

    path('guide', views.guide, name='guide'),

    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('add_user/', views.add_user, name='add_user'),
    path('users', views.users_list, name='users_list'),
    path('user/<int:id>', views.user_detail, name='user'),
    path('user/<int:id>/stats/', views.user_stats, name='stats'),
    path('user/<int:id>/delete', views.delete_user, name='delete_user'),
    path('user/<int:id>/edit', views.edit_user, name='edit_user'),

    path('task-status/<str:task_id>/', views.task_status, name='task_status'),
]