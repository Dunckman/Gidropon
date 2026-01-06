from django.core.management.base import BaseCommand
from apps.monitoring.models import DataFromSensors
from services.get_sensors_data import fetch_remote_sensor_data

class Command(BaseCommand):
    help = 'Импорт данных с датчиков Home Assistant'

    def handle(self, *args, **options):
        try:
            self.stdout.write("Подключение к серверу...")

            # 1. Получение данных (Вся логика "там")
            data = fetch_remote_sensor_data()

            if not data:
                self.stdout.write(self.style.WARNING("Данные не получены (пустой ответ)"))
                return

            self.stdout.write(f"Получены сырые данные: {data}")

            # 2. Сохранение в БД
            log_entry = DataFromSensors.objects.create(
                lux=self._clean(data.get('lux')),
                air_temp=self._clean(data.get('temp_air')),
                sol_temp=self._clean(data.get('temp_water')),
                humidity=self._clean(data.get('humidity')),
                ec=self._clean(data.get('ec')),
                ph=self._clean(data.get('ph')),
                water_level=self._clean(data.get('level')),
            )

            self.stdout.write(self.style.SUCCESS(f"Успешно сохранено! ID: {log_entry.data_id}"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Ошибка: {e}"))

    def _clean(self, value):
        """Конвертирует строки в float или None"""
        if value in [None, 'unavailable', 'unknown', '']:
            return None
        try:
            return float(value)
        except ValueError:
            return None