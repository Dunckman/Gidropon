from django.contrib import admin
from .models import *

admin.site.register(Sensor)
admin.site.register(NormalValues)
admin.site.register(DataFromSensors)
admin.site.register(Solution)
admin.site.register(Accident)