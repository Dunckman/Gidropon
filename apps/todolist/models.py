from django.core.validators import MinValueValidator
from django.db import models
from django.core.exceptions import ValidationError

MAX_TITLE_LENGTH = 25
MAX_PERIODICITY_LENGTH = 15
MAX_STATUS_LENGTH = 15
MAX_CODE_LENGTH = 10

class Plant(models.Model):
    plant_id = models.BigAutoField(
        primary_key=True,
        verbose_name="ID растения"
    )
    title = models.CharField(
        max_length=MAX_TITLE_LENGTH,
        null=False,
        blank=False,
        verbose_name="Навзание растения",
        help_text="Введите название растения"
    )
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name="Описание растения",
        help_text="Введите описание растения"
    )

    def __str__(self):
        return f"{self.title}"

    class Meta:
        db_table = "plants"
        verbose_name = "Растение"
        verbose_name_plural = "Растения"

class Location(models.Model):
    location_id = models.BigAutoField(
        primary_key=True,
        verbose_name="ID локации"
    )
    code = models.CharField(
        max_length=MAX_CODE_LENGTH,
        null=False,
        blank=False,
        verbose_name="Код локации",
        help_text="Введите код локации"
    )
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name="Описание",
        help_text="Введите описание (например, подсказка где найти)"
    )

    def __str__(self):
        return f"{self.code}"

    class Meta:
        db_table = "locations"
        verbose_name = "Локация"
        verbose_name_plural = "Локации"

class Stage(models.Model):
    stage_id = models.BigAutoField(
        primary_key=True,
        verbose_name="Стадия роста"
    )
    plant = models.ForeignKey(
        Plant,
        on_delete=models.CASCADE,
        verbose_name="Растение",
        help_text="Выберите растение из списка"
    )
    title = models.CharField(
        max_length=MAX_TITLE_LENGTH,
        null=False,
        blank=False,
        verbose_name="Название",
        help_text="Введите название"
    )
    duration = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        null=False,
        blank=False,
        verbose_name="Продолжительность в днях",
        help_text="Введите продолжительность в днях"
    )
    start_day = models.IntegerField(
        validators=[MinValueValidator(0)],
        null=True,
        blank=True,
        default=0,
        verbose_name="Начальный день",
        help_text="Будет заполнено автоматически"
    )
    finish_day = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        null=True,
        blank=True,
        verbose_name="Конечный день",
        help_text="Будет заполнено автоматически"
    )
    order = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        null=False,
        blank=False,
        verbose_name="Порядок в цикле роста",
        help_text="Введите порядок в цикле роста"
    )

    def clean(self):
        # Обязательно вызываем родительский метод
        super().clean()

        # Проверяем, заполнены ли оба поля (чтобы не упасть с ошибкой, если одно None)
        if self.start_day is not None and self.finish_day is not None:

            # ВАША ЛОГИКА СРАВНЕНИЯ
            if self.finish_day < self.start_day:
                # Выбрасываем ошибку.
                # Важно: используем словарь, чтобы ошибка привязалась
                # к конкретному полю (например, в админке она будет подсвечивать max_value)
                raise ValidationError({
                    'finish_day': 'Конечный день не может быть меньше начального.'
                })

    def save(self, *args, **kwargs):
        # Опционально: можно форсировать вызов валидации при каждом сохранении
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.plant.title})"

    class Meta:
        db_table = "stages"
        verbose_name = "Стадия роста"
        verbose_name_plural = "Стадии роста"

class Action(models.Model):
    class Periodicity(models.TextChoices):
        ONCE = "once", "Однократно"
        EVERY_DAY = "every_day", "Каждый день"
        EVERY_N_DAY = "every_n_day", "Каждые N дней"

    action_id = models.BigAutoField(
        primary_key=True,
        verbose_name="ID действия"
    )
    stage = models.ForeignKey(
        Stage,
        on_delete=models.CASCADE,
        verbose_name="Стадия роста",
        help_text="Выберите стадию роста из списка"
    )
    title = models.CharField(
        max_length=MAX_TITLE_LENGTH,
        null=False,
        blank=False,
        verbose_name="Название",
        help_text="Введите название"
    )
    periodicity = models.CharField(
        choices=Periodicity.choices,
        default=Periodicity.EVERY_DAY,
        max_length=MAX_PERIODICITY_LENGTH,
        null=False,
        blank=False,
        verbose_name="Периодичность",
        help_text="Выберите периодичность из списка"
    )
    interval = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        null=True,
        blank=True,
        verbose_name="Интервал дней",
        help_text="Введите интервал дней N (только для периодичности \"Каждые N дней\")"
    )
    instruction = models.TextField(
        null=True,
        blank=True,
        verbose_name="Инструкция",
        help_text="Введите инструкцию"
    )

    def __str__(self):
        return f"{self.title} ({self.stage.plant.title})"

    class Meta:
        db_table = "actions"
        verbose_name = "Действие"
        verbose_name_plural = "Действия"

class Planting(models.Model):
    planting_id = models.BigAutoField(
        primary_key=True,
        verbose_name="ID посадки"
    )
    plant = models.ForeignKey(
        Plant,
        on_delete=models.CASCADE,
        verbose_name="Растение",
        help_text="Выберите растение из списка"
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        verbose_name="Локация",
        help_text="Выберите локацию из списка"
    )
    datetime = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата и время посадки",
        help_text="Выберите дату и время посадки"
    )

    def __str__(self):
        return f"{self.plant.title} ({self.datetime.strftime("%H:%M:%S %d.%m.%Y")})"

    class Meta:
        db_table = "plantings"
        verbose_name = "Посадка"
        verbose_name_plural = "Посадки"

class Task(models.Model):
    class Status(models.TextChoices):
        AWAIT = "await", "Ожидает"
        DONE = "done", "Выполнено"
        MISSED = "missed", "Просрочено"

    task_id = models.BigAutoField(
        primary_key=True,
        verbose_name="ID задачи"
    )
    planting = models.ForeignKey(
        Planting,
        on_delete=models.CASCADE,
        verbose_name="Посадка",
        help_text="Выберите посадку из списка"
    )
    action = models.OneToOneField(
        Action,
        on_delete=models.CASCADE,
        verbose_name="Действие",
        help_text="Выберите действие из списка"
    )
    date = models.DateField(
        auto_now_add=True,
        verbose_name="Дата и время задачи",
        help_text="Выберите дату и время задачи"
    )
    status = models.CharField(
        choices=Status.choices,
        default=Status.AWAIT,
        max_length=MAX_STATUS_LENGTH,
        null=False,
        blank=False,
        verbose_name="Статус",
        help_text="Выберите статус из списка"
    )
    eliminated_datetime = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Время и дата выполнения задачи",
        help_text="Выберите дату и время выполнения задачи"
    )

    class Meta:
        db_table = "tasks"
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"