from django.urls import path
from . import views

urlpatterns = [
    path('add_dfs/', views.add_dfs, name='add_dfs'),
    path('add_solution/', views.add_solution, name='add_solution'),

    path('', views.monitoring, name='monitoring'),
]