from django_celery_beat.models import IntervalSchedule


SENSORS_DATA = [
    {
        "sensor_id": 1,
        "parameter": "Влажность воздуха",
        "unit": "%",
        "description": "Фиксирует  изменения влажности воздуха в зоне роста растения",
    },
    {
        "sensor_id": 2,
        "parameter": "Температура воздуха",
        "unit": "°C",
        "description": "Фиксирует  изменения температуры воздуха в зоне роста растения",
    },
    {
        "sensor_id": 3,
        "parameter": "Температура раствора",
        "unit": "°C",
        "description": "Фиксирует  изменения температуры питательного раствора в зоне корней растения",
    },
    {
        "sensor_id": 4,
        "parameter": "Уровень раствора в баке",
        "unit": "%",
        "description": "Фиксирует  изменения уровня питательного раствора в баке",
    },
    {
        "sensor_id": 5,
        "parameter": "EC",
        "unit": "мсим/см",
        "description": "Фиксирует  изменения концентрации солей в питательном растворе в баке",
    },
    {
        "sensor_id": 6,
        "parameter": "Lux",
        "unit": "Люкс",
        "description": "Фиксирует  изменения освещённости в зоне роста растения",
    },
    {
        "sensor_id": 7,
        "parameter": "pH",
        "unit": "Пш",
        "description": "Фиксирует  изменения кислотно-щелочного баланса в питательном растворе в баке",
    },
]

NORMAL_VALUES_DATA = [
    {
        "sensor_id": 1,
        "minimum": 15.5,
        "maximum": 19.0,
        "optimum": 17.0,
        "critical_minimum": 15.0,
        "critical_maximum": 20.0,
    },
    {
        "sensor_id": 2,
        "minimum": 18.0,
        "maximum": 24.0,
        "optimum": 21.0,
        "critical_minimum": 14.0,
        "critical_maximum": 28.0,
    },
    {
        "sensor_id": 3,
        "minimum": 7.0,
        "maximum": 15.0,
        "optimum": 11.0,
        "critical_minimum": 3.0,
        "critical_maximum": 18.0,
    },
    {
        "sensor_id": 4,
        "minimum": 30.0,
        "maximum": 90.0,
        "optimum": 60.0,
        "critical_minimum": 25.0,
        "critical_maximum": 100.0,
    },
    {
        "sensor_id": 5,
        "minimum": 0.3,
        "maximum": 2.5,
        "optimum": 1.5,
        "critical_minimum": 0.0,
        "critical_maximum": 5.0,
    },
    {
        "sensor_id": 6,
        "minimum": 40.0,
        "maximum": 150.0,
        "optimum": 100.0,
        "critical_minimum": 0.0,
        "critical_maximum": 350.0,
    },
    {
        "sensor_id": 7,
        "minimum": -0.65,
        "maximum": 2.0,
        "optimum": 0.8,
        "critical_minimum": -1.0,
        "critical_maximum": 4.0,
    },
]

CRONTAB_DATA = [
    {
        "minute": "0",
        "hour": "4",
        "day_of_week": "*",
        "day_of_month": "*",
        "month_of_year": "*",
        "timezone": "Europe/London",
    },
]

INTERVAL_DATA = [
    {
        "every": 1,
        "period": IntervalSchedule.HOURS,
    },
    {
        "every": 30,
        "period": IntervalSchedule.DAYS,
    }
]

PERIODIC_TASKS_DATA = [
    {
        "name": "Cleanup old celery results",
        "task": "apps.users.tasks.cleanup_old_task_results",
        "description": "Cleanup old task results.",
        "schedule": "daily_04_00",
        "expire_seconds": None,
    },
    {
        "name": "Today's tasks",
        "task": "apps.todolist.tasks.save_tasks_for_today",
        "description": "Generate tasks for today.",
        "schedule": "daily_04_00",
        "expire_seconds": None,
    },
    {
        "name": "Check sensors data",
        "task": "apps.monitoring.tasks.check_accident",
        "description": "Check sensors and detect accidents.",
        "schedule": "each_3_hours",
        "expire_seconds": 3000,
    },
    {
        "name": "celery.backend_cleanup",
        "task": "celery.backend_cleanup",
        "description": "Built-in backend cleanup.",
        "schedule": "daily_04_00",
        "expire_seconds": 43200,
    },
    {
        "name": "Make database backup",
        "task": "apps.users.tasks.make_backup_celery",
        "description": "Make database backup.",
        "schedule": "daily_04_00",
        "expire_seconds": None,
    },
    {
        "name": "Delete old backups",
        "task": "apps.users.tasks.delete_old_backups",
        "description": "Delete old backups.",
        "schedule": "each_30_days",
        "expire_seconds": None,
    },
]