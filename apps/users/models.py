from django.db import models
from django.contrib.auth.models import AbstractUser

class UserGH(AbstractUser):
    surname = models.CharField(
        max_length=15,
        blank=False,
        null=False,
        verbose_name='Фамилия',
        help_text='Введите Вашу фамилию'
    )
    name = models.CharField(
        max_length=15,
        blank=False,
        null=False,
        verbose_name='Имя',
        help_text='Введите Ваше имя'
    )
    patronymic = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        verbose_name='Отчество',
        help_text='Введите Ваше отчество (если имеется)'
    )
    phone = models.CharField(
        max_length=14,
        blank=False,
        null=False,
        verbose_name='Телефон',
        help_text='Введите Ваш телефон'
    )
    post = models.CharField(
        max_length=15,
        blank=False,
        null=False,
        verbose_name='Должность',
        help_text='Введите Вашу должность'
    )

    REQUIRED_FIELDS = ['email', 'surname', 'name', 'phone', 'post']

    def __str__(self):
        return f"{self.surname} {self.name} ({self.email})"

    class Meta:
        db_table = 'users'
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'