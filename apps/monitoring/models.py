from django.db import models

class Sensor(models.Model):
    sensor_id = models.BigAutoField(verbose_name='ID датчика')
    title = models.CharField(
        max_length=25,
        null=False,
        blank=False,
        verbose_name='',
        help_text='',
    )
    code = models.CharField(
        max_length=15,
        null=False,
        blank=False,
        verbose_name='',
        help_text='',
    )
    unit = models.CharField(
        max_length=25,
        null=False,
        blank=False,
        verbose_name='',
        help_text='',
    )
    description = models.TextField(
        null=False,
        blank=False,
        verbose_name='',
        help_text='',
    )
