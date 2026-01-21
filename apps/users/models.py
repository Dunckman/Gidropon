from django.db import models
from django.contrib.auth.models import AbstractUser

MAX_SURNAME_LENGTH = 25
MAX_NAME_LENGTH = 25
MAX_PATRONYMIC_LENGTH = 25
MAX_PHONE_LENGTH = 15
MAX_POST_LENGTH = 35

class UserGH(AbstractUser):
    surname = models.CharField(
        max_length=MAX_SURNAME_LENGTH,
        blank=False,
        null=False,
        verbose_name='Фамилия',
        help_text='Введите Вашу фамилию'
    )
    name = models.CharField(
        max_length=MAX_NAME_LENGTH,
        blank=False,
        null=False,
        verbose_name='Имя',
        help_text='Введите Ваше имя'
    )
    patronymic = models.CharField(
        max_length=MAX_PATRONYMIC_LENGTH,
        blank=True,
        null=True,
        verbose_name='Отчество',
        help_text='Введите Ваше отчество (если имеется)'
    )
    phone = models.CharField(
        max_length=MAX_PHONE_LENGTH,
        blank=False,
        null=False,
        verbose_name='Телефон',
        help_text='Введите Ваш телефон'
    )
    post = models.CharField(
        max_length=MAX_POST_LENGTH,
        blank=False,
        null=False,
        verbose_name='Должность',
        help_text='Введите Вашу должность'
    )

    REQUIRED_FIELDS = ['email', 'surname', 'name', 'patronymic', 'phone', 'post']

    def __str__(self):
        return f"{self.surname} {self.name} ({self.email})"

    class Meta:
        db_table = 'users'
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'