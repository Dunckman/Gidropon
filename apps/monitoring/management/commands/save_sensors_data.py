from django.core.management.base import BaseCommand
from services.sensors_data_logic import save_current_data, EmptyData


class Command(BaseCommand):
    help = 'Импорт данных с датчиков Home Assistant'


    def handle(self, *args, **options):
        self.stdout.write("Подключение к серверу...")

        try:
            new_dfs = save_current_data()

            self.stdout.write(self.style.SUCCESS(f"Успешно сохранено! ID: {new_dfs.data_id}"))
        except EmptyData:
            self.stdout.write(self.style.ERROR("Получены пустые данные."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Ошибка: {e}"))