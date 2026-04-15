from celery import shared_task
from django.db import IntegrityError
from services.tasks_logic import get_tasks_for_today


@shared_task
def save_tasks_for_today():
    try:
        tasks = get_tasks_for_today()
        for task in tasks:
            try:
                task.save()
            except IntegrityError:
                pass
    except Exception as e:
        print(f"Ошибка: {e}")