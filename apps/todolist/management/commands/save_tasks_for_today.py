from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError
from services.tasks_logic import get_tasks_for_today

class NonTasksForTodayError(Exception):
    pass

class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write("Подключение к серверу...")

        try:
            tasks = get_tasks_for_today()
            successful_add = 0
            for task in tasks:
                try:
                    task.save()
                    successful_add += 1
                except IntegrityError:
                    pass

            if successful_add == 0:
                self.stdout.write(self.style.SUCCESS(f"На сегодня новых заданий нет."))
                return
            self.stdout.write(self.style.SUCCESS(f"Успешно сохранено! Добавлено {successful_add} задач(-чи)."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Ошибка: {e}"))