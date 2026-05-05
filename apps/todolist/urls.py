from django.urls import path, re_path
from . import views

urlpatterns = [
    path('plant/add/', views.add_plant, name='add_plant'),
    path('plant/<int:id>/', views.plant_detail, name='plant'),
    path('plant/<int:id>/edit/', views.edit_plant, name='edit_plant'),
    path('plant/<int:id>/delete/', views.delete_plant, name='delete_plant'),
    path('plants', views.plants_list, name='plants_list'),

    path('location/add/', views.add_location, name='add_location'),
    path('location/<int:id>/', views.location_detail, name='location'),
    path('location/<int:id>/edit/', views.edit_location, name='edit_location'),
    path('location/<int:id>/delete/', views.delete_location, name='delete_location'),
    path('locations', views.locations_list, name='locations_list'),

    path('stage/add/', views.add_stage, name='add_stage'),
    path('stage/<int:id>/', views.stage_detail, name='stage'),
    path('stage/<int:id>/edit/', views.edit_stage, name='edit_stage'),
    path('stages', views.stages_list, name='stages_list'),

    path('action/add/', views.add_action, name='add_action'),
    path('action/<int:id>/', views.action_detail, name='action'),
    path('action/<int:id>/edit/', views.edit_action, name='edit_action'),
    path('actions', views.actions_list, name='actions_list'),

    path('planting/add/', views.add_planting, name='add_planting'),
    path('planting/<int:id>/', views.planting_detail, name='planting'),
    path('planting/<int:id>/dead/', views.mark_planting_dead, name='planting_dead'),
    path('plantings', views.plantings_list, name='plantings_list'),

    path('task/<int:id>/', views.task_detail, name='task'),
    path('tasks', views.tasks_list, name='tasks_list'),
    path('task/<int:id>/done/', views.mark_task_done, name="mark_task_done"),

    path('', views.todolist, name='todolist'),
    path('missed', views.missed_tasks, name='missed_tasks'),
    path(r'add-tasks/', views.add_today_tasks, name='add_tasks'),
    # re_path(r'add-tasks/(?P<target_date>\d{4}-\d{2}-\d{2})/', views.add_new_tasks, name='add_tasks'),
]