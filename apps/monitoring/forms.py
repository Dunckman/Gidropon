from django import forms
from apps.monitoring.models import *


class SensorForm(forms.Form):
    parameter = forms.CharField(
        widget=forms.TextInput(),
        max_length=MAX_TITLE_LENGTH,
        required=True,
        label="Параметр",
        help_text="Введите параметр датчика",
    )
    unit = forms.CharField(
        widget=forms.TextInput(),
        max_length=MAX_UNIT_LENGTH,
        required=True,
        label="Единица измерения",
        help_text="Введите единицу измерения",
    )
    description = forms.CharField(
        widget=forms.Textarea(),
        required=False,
        label="Описание",
        help_text="Введите описание",
    )


class NormalValuesForm(forms.Form):
    # sensor = forms.ModelChoiceField(
    #     queryset=Sensor.objects.all(),
    #     widget=forms.Select(),
    #     required=True,
    #     label="Параметр",
    #     help_text="Выберите параметр из списка"
    # )
    minimum = forms.FloatField(
        widget=forms.NumberInput(),
        required=True,
        label="Минимально допустимое значение",
        help_text="Введите минимально допустимое значение"
    )
    maximum = forms.FloatField(
        widget=forms.NumberInput(),
        required=True,
        label="Максимально допустимое значение",
        help_text="Введите максимально допустимое значение"
    )
    optimum = forms.FloatField(
        widget=forms.NumberInput(),
        required=True,
        label="Оптимальное значение",
        help_text="Введите оптимальное значение"
    )
    critical_minimum = forms.FloatField(
        widget=forms.NumberInput(),
        required=True,
        label="Критический минимум",
        help_text="Введите критический минимум"
    )
    critical_maximum = forms.FloatField(
        widget=forms.NumberInput(),
        required=True,
        label="Критический максимум",
        help_text="Введите критический максимум"
    )


class DataFromSensorsForm(forms.Form):
    humidity = forms.FloatField(
        widget=forms.NumberInput(),
        required=True,
        label="Влажность воздуха",
        help_text="Введите влажность воздуха"
    )
    air_temp = forms.FloatField(
        widget=forms.NumberInput(),
        required=True,
        label="Температура воздуха",
        help_text="Введите температуру воздуха"
    )
    sol_temp = forms.FloatField(
        widget=forms.NumberInput(),
        required=True,
        label="Температура раствора",
        help_text="Введите температуру раствора"
    )
    water_level = forms.FloatField(
        widget=forms.NumberInput(),
        required=True,
        label="Уровень раствора в баке",
        help_text="Введите уровень раствора в баке"
    )
    ec = forms.FloatField(
        widget=forms.NumberInput(),
        required=True,
        label="EC",
        help_text="Введите EC"
    )
    lux = forms.FloatField(
        widget=forms.NumberInput(),
        required=True,
        label="Lux",
        help_text="Введите Lux"
    )
    ph = forms.FloatField(
        widget=forms.NumberInput(),
        required=True,
        label="pH",
        help_text="Введите pH"
    )


class SolutionForm(forms.Form):
    recommendation = forms.CharField(
        widget=forms.Textarea(),
        required=True,
        label="Рекомендация для устранения аварии",
        help_text="Введите рекомендацию для устранению аварии"
    )
    arguments = forms.CharField(
        widget=forms.Textarea(),
        required=True,
        label="Аргументы для устранения аварии",
        help_text="Введите аргументы для устранения аварии"
    )
    comment = forms.CharField(
        widget=forms.Textarea(),
        required=False,
        label="Комментарий об устранении аварии",
        help_text="Введите комментарий об устранении аварии"
    )