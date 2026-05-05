from apps.monitoring.models import Accident, Solution, DataFromSensors
from apps.todolist.models import Planting

def delete_objects():
    Planting.objects.all().delete()

    Accident.objects.all().delete()
    Solution.objects.all().delete()
    DataFromSensors.objects.all().delete()