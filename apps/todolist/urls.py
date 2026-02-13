from django.urls import path
from . import views

urlpatterns = [
    path('add_plant/', views.add_plant, name='add_plant'),
    path('add_location/', views.add_location, name='add_location'),
    path('add_stage/', views.add_stage, name='add_stage'),
    path('add_action/', views.add_action, name='add_action'),
    path('add_planting/', views.add_planting, name='add_planting'),

    path('plant/<int:plant_id>/', views.plant_detail, name='plant_detail'),
    path('location/<int:location_id>/', views.location_detail, name='location_detail'),
    path('stage/<int:stage_id>/', views.stage_detail, name='stage_detail'),
    path('action/<int:action_id>/', views.action_detail, name='action_detail'),
    path('planting/<int:planting_id>/', views.planting_detail, name='planting_detail'),

    path('', views.tasks_list, name='todolist'),
    path('missed_tasks/', views.missed_tasks, name='missed_tasks'),
    path('task/<int:task_id>/', views.task_detail, name='task_detail'),
    path("task/<int:task_id>/mark-done/", views.mark_task_done, name="mark_task_done"),
]