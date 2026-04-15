from django.core.management.base import BaseCommand
from apps.monitoring.models import DataFromSensors
from services.llm.rag import check_data, NotAccident, NoDataForGenerate
from services.sensors_data_logic import save_current_data, EmptyData, HomeAssistantNotExists


class Command(BaseCommand):
    help = 'Проверка показателей датчиков на их нарушение'


    def add_arguments(self, parser):
        parser.add_argument('--id', type=int, default=None)


    def handle(self, *args, **options):
        dfs_id = options['id']

        self.stdout.write("Подключение к серверу...")

        try:
            if dfs_id is None:
                dfs = save_current_data()
                self.stdout.write(self.style.SUCCESS(f"Данные датчиков успешно сохранены! ID: {dfs.data_id}.\n\n"))
            elif dfs_id == -1:
                dfs = DataFromSensors.objects.last()
                self.stdout.write(self.style.SUCCESS(f"Обрабатываются последние имеющиеся данные (ID: {dfs.data_id}).\n\n"))
            else:
                dfs = DataFromSensors.objects.get(data_id=dfs_id)
                self.stdout.write(self.style.SUCCESS(f"Обрабатывабтся данные с ID: {dfs.data_id}.\n\n"))

            accident, solution = check_data(dfs)
        except NoDataForGenerate:
            self.stdout.write(self.style.ERROR(
                "На основе базы данных о прошлых авариях невозможно создать корректное решение текущей аварии. " +
                "Пожалуйста внесите данные о прошлых авариях вручную."
            ))
        except NotAccident:
            self.stdout.write(self.style.SUCCESS("Все показатели датчиков корректны."))
        except HomeAssistantNotExists:
            self.stdout.write(self.style.SUCCESS("В Вашей системе не установлен модуль HomeAssistant."))
        except EmptyData:
            self.stdout.write(self.style.ERROR("Получены пустые данные."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Ошибка: {e}."))
        else:
            self.stdout.write(self.style.SUCCESS("Зарегистрирована следующая авария:"))
            self.stdout.write(self.style.SUCCESS(accident.description + '\n\n'))
            self.stdout.write(self.style.SUCCESS(solution.full_info()))