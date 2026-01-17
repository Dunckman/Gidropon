from django.urls import path
from . import views

urlpatterns = [
    path('add_plant/', views.add_plant, name='add_plant'),
]