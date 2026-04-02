from django.db import models
from django.conf import settings
from pgvector.django import VectorField

VECTOR_DIMENSION = 512
MAX_TITLE_LENGTH = 25
MAX_CODE_LENGTH = 15
MAX_UNIT_LENGTH = 10
MAX_STATUS_LENGTH = 15

class Sensor(models.Model):
    sensor_id = models.BigAutoField(
        primary_key=True,
        verbose_name="ID датчика"
    )
    parameter = models.CharField(
        max_length=MAX_TITLE_LENGTH,
        unique=True,
        null=False,
        blank=False,
        verbose_name="Параметр",
        help_text="Введите параметр датчика",
    )
    code = models.CharField(
        max_length=MAX_CODE_LENGTH,
        null=False,
        blank=False,
        verbose_name="Кодовое сокращение",
        help_text="Введите кодовое сокращение",
    )
    unit = models.CharField(
        max_length=MAX_UNIT_LENGTH,
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

    def get_descr_short(self):
        if len(self.description) > 65:
            return self.description[:65] + "..."
        return self.description

    class Meta:
        db_table = "sensors"
        verbose_name = "Датчик"
        verbose_name_plural = "Датчики"

class NormalValues(models.Model):
    values_id = models.BigAutoField(
        primary_key=True,
        verbose_name="ID нормальных значений"
    )
    sensor = models.OneToOneField(
        Sensor,
        on_delete=models.CASCADE,
        unique=True,
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

    def dict_data(self):
        return {
            "ID": self.data_id,
            "Дата и время": self.datetime.strftime("%H:%M:%S %d.%m.%Y"),
            "Влажность воздуха": self.humidity,
            "Температура воздуха": self.air_temp,
            "Температура раствора": self.sol_temp,
            "Уровень раствора в баке": self.water_level,
            "EC": self.ec,
            "Lux": self.lux,
            "pH": self.ph
        }

    def html_data(self):
        html = f"""
            <table>
                <thead>
                    <tr>
                        <td>Показатель</td>
                        <td>Влажность воздуха</td>
                        <td>Температура воздуха</td>
                        <td>Температура раствора</td>
                        <td>Уровень раствора в баке</td>
                        <td>EC</td>
                        <td>Lux</td>
                        <td>pH</td>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Значение</td>
                        <td>{self.humidity}</td>
                        <td>{self.air_temp}</td>
                        <td>{self.sol_temp}</td>
                        <td>{self.water_level}</td>
                        <td>{self.ec}</td>
                        <td>{self.lux}</td>
                        <td>{self.ph}</td>
                    </tr>
                </tbody>
            </table> 
        """
        return html

    class Meta:
        db_table = "data_from_sensors"
        verbose_name = "Показания датчиков"
        verbose_name_plural = "Показания датчиков"

class Solution(models.Model):
    solution_id = models.BigAutoField(
        primary_key=True,
        verbose_name="ID решения"
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
        null=True,
        blank=True,
        default="Авария устранена в соответствии с рекомендацией",
        verbose_name="Комментарий об устранении аварии",
        help_text="Введите комментарий об устранении аварии"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        verbose_name="Аварию устранил пользователь",
        help_text="Выберите пользователя, устранившего аварию, из списка"
    )

    def full_info(self):
        return (f"Рекомендации:\n"
                f"{self.recommendation}\n"
                f"Аргументы:\n"
                f"{self.arguments}\n")

    def get_rec_short(self):
        if len(self.recommendation) > 50:
            return self.recommendation[:50] + "..."
        return self.recommendation

    def get_arg_short(self):
        if len(self.arguments) > 50:
            return self.arguments[:50] + "..."
        return self.arguments

    def get_com_short(self):
        if len(self.comment) > 50:
            return self.comment[:50] + "..."
        return self.comment

    def __str__(self):
        return f"ID решения: {self.solution_id}"

    class Meta:
        db_table = "solutions"
        verbose_name = "Описание устранения аварии"
        verbose_name_plural ="Описания устранения аварий"

class Accident(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "Новая"
        ELIMINATED = "eliminated", "Устранена"
        NOT_ELIMINATED = "not_eliminated", "Не устранена"

    accident_id = models.BigAutoField(
        primary_key=True,
        verbose_name="ID аварии"
    )
    data_from_sensors = models.OneToOneField(
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
    solution = models.OneToOneField(
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
        max_length=MAX_STATUS_LENGTH,
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

    def get_descr_short(self):
        if len(self.description) > 65:
            return self.description[:65] + "..."
        return self.description

    def __str__(self):
        return f"{self.description}"

    class Meta:
        db_table = "accidents"
        verbose_name = "Авария"
        verbose_name_plural = "Аварии"