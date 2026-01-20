from django.urls import path
from . import views

urlpatterns = [
    path('add_plant/', views.add_plant, name='add_plant'),
    path('add_location/', views.add_location, name='add_location'),
    path('add_stage/', views.add_stage, name='add_stage'),
    path('add_action/', views.add_action, name='add_action'),
    path('add_planting/', views.add_planting, name='add_planting'),
    path('rel_acts/', views.relevant_actions_list, name='rel_acts'),
]