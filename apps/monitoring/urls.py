from django.urls import path
from . import views

urlpatterns = [
    path('sensor/<int:id>/', views.sensor_detail, name='sensor'),
    path('sensors/', views.sensors_list, name='sensors_list'),
    path('sensor/<int:id>/edit', views.edit_sensor, name='edit_sensor'),

    path('normal-values/<int:id>/', views.normals_detail, name='normal_values'),
    path('normals/', views.normals_list, name='normals_list'),
    path('normals/<int:id>/edit/', views.edit_normals, name='edit_normals'),

    path('dfs/add/', views.add_dfs, name='add_dfs'),
    path('dfs/<int:id>/', views.dfs_detail, name='dfs'),
    path('dfses/', views.dfs_list, name='dfs_list'),

    path('solution/add', views.add_solution, name='add_solution'),
    path('solution/<int:id>/', views.solution_detail, name='solution'),
    path('solutions/', views.solutions_list, name='solutions_list'),

    path('accident/<int:id>/', views.accident_detail, name='accident'),
    path('accidents/', views.accidents_list, name='accidents_list'),
    path('accident/<int:id>/done/<str:comment>/', views.mark_accident_done, name='mark_accident_done'),

    path('', views.monitoring, name='monitoring'),
    path('check-new/', views.check_new, name='check_new'),
    path('check-new/<str:task_id>/cancel/', views.cancel_check_new, name='cancel_check_new'),
]
