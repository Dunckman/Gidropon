from django.urls import path
from . import views

urlpatterns = [
    path('add_plant/', views.add_plant, name='add_plant'),
    path('add_location/', views.add_location, name='add_location'),
    path('add_stage/', views.add_stage, name='add_stage'),
    path('add_action/', views.add_action, name='add_action'),
    path('add_planting/', views.add_planting, name='add_planting'),

    path('plant/<int:id>/', views.plant_detail, name='plant'),
    path('location/<int:id>/', views.location_detail, name='location'),
    path('stage/<int:id>/', views.stage_detail, name='stage'),
    path('action/<int:id>/', views.action_detail, name='action'),
    path('planting/<int:id>/', views.planting_detail, name='planting'),

    path('edit_plant/<int:id>/', views.edit_plant, name='edit_plant'),
    path('edit_location/<int:id>/', views.edit_location, name='edit_location'),
    path('edit_stage/<int:id>/', views.edit_stage, name='edit_stage'),
    path('edit_action/<int:id>/', views.edit_action, name='edit_action'),
    path('edit_planting/<int:id>/', views.edit_planting, name='edit_planting'),

    path('plants', views.plants_list, name='plants_list'),
    path('locations', views.locations_list, name='locations_list'),
    path('stages', views.stages_list, name='stages_list'),
    path('actions', views.actions_list, name='actions_list'),
    path('plantings', views.plantings_list, name='plantings_list'),
    path('tasks', views.tasks_list, name='tasks_list'),

    path('', views.todolist, name='todolist'),
    path('guide', views.guide, name='guide'),

    path('missed_tasks/', views.missed_tasks, name='missed_tasks'),
    path('task/<int:id>/', views.task_detail, name='task'),
    path("task/<int:id>/mark-done/", views.mark_task_done, name="mark_task_done"),
]