from django.core.management.base import BaseCommand
from django.db import transaction
from django_celery_beat.models import CrontabSchedule, PeriodicTask, PeriodicTasks
from apps.monitoring.models import NormalValues, Sensor
from services.base_data_in_db import *


class Command(BaseCommand):
    help = (
        "Initializing the database with basic data."
    )

    @transaction.atomic
    def handle(self, *args, **options):
        self._upsert_sensors()
        self._upsert_normal_values()
        schedules = self._upsert_schedules()
        self._upsert_periodic_tasks(schedules)
        PeriodicTasks.changed(None)
        self.stdout.write(self.style.SUCCESS("Base data bootstrap completed."))

    def _upsert_sensors(self):
        for item in SENSORS_DATA:
            sensor_id = item["sensor_id"]
            defaults = {
                "parameter": item["parameter"],
                "unit": item["unit"],
                "description": item["description"],
            }
            Sensor.objects.update_or_create(sensor_id=sensor_id, defaults=defaults)

    def _upsert_normal_values(self):
        for item in NORMAL_VALUES_DATA:
            sensor = Sensor.objects.get(sensor_id=item["sensor_id"])
            defaults = {
                "minimum": item["minimum"],
                "maximum": item["maximum"],
                "optimum": item["optimum"],
                "critical_minimum": item["critical_minimum"],
                "critical_maximum": item["critical_maximum"],
            }
            NormalValues.objects.update_or_create(sensor=sensor, defaults=defaults)

    def _upsert_schedules(self):
        daily_04_00, _ = CrontabSchedule.objects.get_or_create(**CRONTAB_DATA[0])
        yearly_01_01_04_00, _ = CrontabSchedule.objects.get_or_create(**CRONTAB_DATA[1])
        each_3_hours, _ = IntervalSchedule.objects.get_or_create(**INTERVAL_DATA[0])
        each_30_days, _ = IntervalSchedule.objects.get_or_create(**INTERVAL_DATA[1])

        return {
            "daily_04_00": {"crontab": daily_04_00, "interval": None},
            "yearly_01_01_04_00": {"crontab": yearly_01_01_04_00, "interval": None},
            "each_3_hours": {"crontab": None, "interval": each_3_hours},
            "each_30_days": {"crontab": None, "interval": each_30_days},
        }

    def _upsert_periodic_tasks(self, schedules):
        for item in PERIODIC_TASKS_DATA:
            schedule = schedules[item["schedule"]]
            defaults = {
                "task": item["task"],
                "args": "[]",
                "kwargs": "{}",
                "enabled": True,
                "description": item["description"],
                "one_off": False,
                "crontab": schedule["crontab"],
                "interval": schedule["interval"],
                "expire_seconds": item["expire_seconds"],
            }
            PeriodicTask.objects.update_or_create(name=item["name"], defaults=defaults)