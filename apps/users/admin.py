from django.contrib import admin
from apps.monitoring.models import *

admin.site.register(UserGH)
admin.site.register(Sensor)
admin.site.register(NormalValues)
admin.site.register(DataFromSensors)
admin.site.register(Solution)
admin.site.register(Accident)