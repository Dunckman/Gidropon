from django.db import models
from apps.users.models import UserGH
from pgvector.django import VectorField

VECTOR_DIMENSION = 3584

class Sensor(models.Model):
    sensor_id = models.BigAutoField(
        primary_key=True,
        verbose_name="ID датчика"
    )
    parameter = models.CharField(
        max_length=25,
        null=False,
        blank=False,
        verbose_name="Параметр",
        help_text="Введите параметр датчика",
    )
    code = models.CharField(
        max_length=15,
        null=False,
        blank=False,
        verbose_name="Кодовое сокращение",
        help_text="Введите кодовое сокращение",
    )
    unit = models.CharField(
        max_length=10,
        null=False,
        blank=False,
        verbose_name="Единица измерения",
        help_text="Введите единицу измерения",
    )
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name="Описание",
        help_text="Введите описание",
    )

    def __str__(self):
        return f"{self.parameter} (ID: {self.sensor_id})"

    class Meta:
        db_table = "sensors"
        verbose_name = "Датчик"
        verbose_name_plural = "Датчики"

class NormalValues(models.Model):
    values_id = models.BigAutoField(
        primary_key=True,
        verbose_name="ID нормальных значений"
    )
    sensor = models.ForeignKey(
        Sensor,
        on_delete=models.CASCADE,
        verbose_name="Параметр",
        help_text="Выберите параметр из списка"
    )
    minimum = models.FloatField(
        null=False,
        blank=False,
        verbose_name="Минимально допустимое значение",
        help_text="Введите минимально допустимое значение"
    )
    maximum = models.FloatField(
        null=False,
        blank=False,
        verbose_name="Максимально допустимое значение",
        help_text="Введите максимально допустимое значение"
    )
    optimum = models.FloatField(
        null=False,
        blank=False,
        verbose_name="Оптимальное значение",
        help_text="Введите оптимальное значение"
    )
    critical_minimum = models.FloatField(
        null=False,
        blank=False,
        verbose_name="Критический минимум",
        help_text="Введите критический минимум"
    )
    critical_maximum = models.FloatField(
        null=False,
        blank=False,
        verbose_name="Критический максимум",
        help_text="Введите критический максимум"
    )

    class Meta:
        db_table = "normal_values"
        verbose_name = "Нормальные значения"
        verbose_name_plural = "Нормальные значения"

class DataFromSensors(models.Model):
    data_id = models.BigAutoField(
        primary_key=True,
        verbose_name="ID данных"
    )
    datetime = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Время и дата показаний",
        help_text="Выберите дату и время показаний"
    )
    humidity = models.FloatField(
        null=False,
        blank=False,
        verbose_name="Влажность воздуха",
        help_text="Введите влажность воздуха"
    )
    air_temp = models.FloatField(
        null=False,
        blank=False,
        verbose_name="Температура воздуха",
        help_text="Введите температуру воздуха"
    )
    sol_temp = models.FloatField(
        null=False,
        blank=False,
        verbose_name="Температура раствора",
        help_text="Введите температуру раствора"
    )
    water_level = models.FloatField(
        null=False,
        blank=False,
        verbose_name="Уровень воды в баке",
        help_text="Введите уровень воды в баке"
    )
    ec = models.FloatField(
        null=False,
        blank=False,
        verbose_name="EC",
        help_text="Введите EC"
    )
    lux = models.FloatField(
        null=False,
        blank=False,
        verbose_name="Lux",
        help_text="Введите Lux"
    )
    ph = models.FloatField(
        null=False,
        blank=False,
        verbose_name="pH",
        help_text="Введите pH"
    )

    def __str__(self):
        return f"{self.datetime.strftime("%H:%M:%S %d.%m.%Y")}"

    class Meta:
        db_table = "data_from_sensors"
        verbose_name = "Показания датчиков"
        verbose_name_plural = "Показания датчиков"

class Solution(models.Model):
    solution_id = models.IntegerField(
        primary_key=True,
        auto_created=False,
        null=False,
        blank=False,
        verbose_name="ID решения",
        help_text="Введите ID решения"
    )
    recommendation = models.TextField(
        null=False,
        blank=False,
        verbose_name="Рекомендация для устранения аварии",
        help_text="Введите рекомендацию для устранению аварии"
    )
    arguments = models.TextField(
        null=False,
        blank=False,
        verbose_name="Аргументы для устранения аварии",
        help_text="Введите аргументы для устранения аварии"
    )
    comment = models.TextField(
        null=False,
        blank=True,
        default="Авария устранена",
        verbose_name="Комментарий об устранении аварии",
        help_text="Введите комментарий об устранении аварии"
    )
    user = models.ForeignKey(
        UserGH,
        on_delete=models.DO_NOTHING,
        verbose_name="Аварию устранил пользователь",
        help_text="Выберите пользователя, устранившего аварию, из списка"
    )

    def full_info(self):
        return (f""
                f"Рекомендация по устранению:\n"
                f"{self.recommendation}\n"
                f"Аргументы:\n"
                f"{self.arguments}\n")

    def __str__(self):
        return f"ID решения: {self.solution_id}"

    class Meta:
        db_table = "solutions"
        verbose_name = "Описание устранения аварии"
        verbose_name_plural ="Описания устранения аварий"

class Accident(models.Model):
    class Status(models.TextChoices):
        NEW = "New", "Новая"
        ELIMINATED = "Eliminated", "Устранена"
        NOT_ELIMINATED = "Not_eliminated", "Не устранена"

    accident_id = models.BigAutoField(
        primary_key=True,
        verbose_name="ID аварии"
    )
    data_from_sensors = models.ForeignKey(
        DataFromSensors,
        on_delete=models.DO_NOTHING,
        verbose_name="Показания датчиков",
        help_text="Выберите показания датчиков по дате из списка"
    )
    description = models.TextField(
        null=False,
        blank=False,
        verbose_name="Описание аварии",
        help_text="Введите устранение аварии"
    )
    solution = models.ForeignKey(
        Solution,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        verbose_name="Устранение аварии",
        help_text="Выберите устранение аварии из списка по ID (оно соответствует ID аварии)"
    )
    status = models.CharField(
        choices=Status.choices,
        default=Status.NEW,
        max_length=15,
        null=False,
        blank=False,
        verbose_name="Статус",
        help_text="Выберите статус из списка"
    )
    eliminated_datetime = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Время и дата устранения аварии",
        help_text="Выберите дату и время устранения аварии"
    )
    embedding = VectorField(
        dimensions=VECTOR_DIMENSION,
        null=False,
        editable=False,
        verbose_name="Эмбеддниг описания аварии"
    )

    def __str__(self):
        return f"{self.description}"

    class Meta:
        db_table = "accidents"
        verbose_name = "Авария"
        verbose_name_plural = "Аварии"