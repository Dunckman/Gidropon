from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError
from services.get_tasks_for_today import get_tasks_for_today

class NonTasksForTodayError(Exception):
    pass

class Command(BaseCommand):
    def handle(self, *args, **options):
        tasks = get_tasks_for_today()
        successful_add = 0
        for task in tasks:
            try:
                task.save()
                successful_add += 1
            except IntegrityError:
                pass
        self.stdout.write(self.style.SUCCESS(f"Успешно сохранено! Добавлено {successful_add} задач(-чи):"))