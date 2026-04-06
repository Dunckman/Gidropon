from django.urls import path
from . import views

urlpatterns = [
    path('add_dfs/', views.add_dfs, name='add_dfs'),
    path('add_solution/', views.add_solution, name='add_solution'),

    path('sensor/<int:id>/', views.sensor_detail, name='sensor'),
    path('normal_values/<int:id>/', views.normals_detail, name='normal_values'),
    path('dfs/<int:id>/', views.dfs_detail, name='dfs'),
    path('solution/<int:id>/', views.solution_detail, name='solution'),
    path('accident/<int:id>/', views.accident_detail, name='accident'),

    path('sensors/', views.sensors_list, name='sensors_list'),
    path('normals/', views.normals_list, name='normals_list'),
    path('dfses/', views.dfs_list, name='dfs_list'),
    path('solutions/', views.solutions_list, name='solutions_list'),
    path('accidents/', views.accidents_list, name='accidents_list'),

    path('', views.monitoring, name='monitoring'),
    path('accident/<int:id>/mark-done/<str:comment>/', views.mark_accident_done, name='mark_accident_done'),
    path('check-new/', views.check_new, name='check_new'),
    path('task-status/<str:task_id>/', views.task_status, name='task_status'),
]