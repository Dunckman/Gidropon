from django.contrib import admin
from apps.monitoring.models import *
from apps.todolist.models import *

admin.site.register(UserGH)

admin.site.register(Sensor)
admin.site.register(NormalValues)
admin.site.register(DataFromSensors)
admin.site.register(Solution)
admin.site.register(Accident)

admin.site.register(Plant)
admin.site.register(Location)
admin.site.register(Stage)
admin.site.register(Action)
admin.site.register(Planting)
admin.site.register(Task)