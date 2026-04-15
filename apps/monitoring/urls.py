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
    path('accident/<int:id>/mark-done/<str:comment>/', views.mark_accident_done, name='mark_accident_done'),

    path('', views.monitoring, name='monitoring'),
    path('check-new/', views.check_new, name='check_new'),

    # path('add_dfs/', views.add_dfs, name='add_dfs'),
    # path('add_solution/', views.add_solution, name='add_solution'),

    # path('sensor/<int:id>/', views.sensor_detail, name='sensor'),
    # path('normal_values/<int:id>/', views.normals_detail, name='normal_values'),
    # path('dfs/<int:id>/', views.dfs_detail, name='dfs'),
    # path('solution/<int:id>/', views.solution_detail, name='solution'),
    path('accident/<int:id>/', views.accident_detail, name='accident'),

    # path('sensors/', views.sensors_list, name='sensors_list'),
    # path('normals/', views.normals_list, name='normals_list'),
    # path('dfses/', views.dfs_list, name='dfs_list'),
    # path('solutions/', views.solutions_list, name='solutions_list'),
    path('accidents/', views.accidents_list, name='accidents_list'),

    path('', views.monitoring, name='monitoring'),
    path('accident/<int:id>/mark-done/<str:comment>/', views.mark_accident_done, name='mark_accident_done'),
    path('check-new/', views.check_new, name='check_new'),

    # path('edit_sensor/<int:id>/', views.edit_sensor, name='edit_sensor'),
    # path('edit_normals/<int:id>/', views.edit_normals, name='edit_normals'),
]