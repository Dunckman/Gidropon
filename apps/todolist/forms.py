from django import forms
from apps.todolist.models import Plant, Stage, Action, Location

MAX_TITLE_LENGTH = 25
MAX_CODE_LENGTH = 10

class PlantForm(forms.Form):
    title = forms.CharField(
        widget=forms.TextInput(),
        max_length=MAX_TITLE_LENGTH,
        required=True,
        label="Название",
        help_text="Введите название растения"
    )
    description = forms.CharField(
        widget=forms.Textarea(),
        required=False,
        label="Описание",
        help_text="Введите описание растения"
    )

class LocationForm(forms.Form):
    code = forms.CharField(
        widget=forms.TextInput(),
        max_length=MAX_TITLE_LENGTH,
        required=True,
        label="Код",
        help_text="Введите код расположения"
    )
    description = forms.CharField(
        widget=forms.Textarea(),
        required=False,
        label="Описание",
        help_text="Введите описание расположения"
    )

class StageForm(forms.Form):
    plant = forms.ModelChoiceField(
        queryset=Plant.objects.all(),
        widget=forms.Select(),
        required=True,
        label="Растение",
        help_text="Выберите растение"
    )
    title = forms.CharField(
        widget=forms.TextInput(),
        max_length=MAX_TITLE_LENGTH,
        required=True,
        label="Название",
        help_text="Введите название стадии"
    )
    duration = forms.IntegerField(
        widget=forms.NumberInput(),
        min_value=1,
        required=True,
        label="Длительность",
        help_text="Введите длительность стадии (в днях)"
    )
    order = forms.IntegerField(
        widget=forms.NumberInput(),
        min_value=1,
        required=True,
        label="Порядок",
        help_text="Введите порядковый номер стадии в общем цикле развития"
    )

class ActionForm(forms.Form):
    stage = forms.ModelChoiceField(
        queryset=Stage.objects.all(),
        widget=forms.Select(),
        required=True,
        label="Стадия роста",
        empty_label="Выберите стадию"
    )
    title = forms.CharField(
        widget=forms.TextInput(),
        max_length=MAX_TITLE_LENGTH,
        required=True,
        label="Название",
        help_text="Введите название действия"
    )
    periodicity = forms.ChoiceField(
        choices=Action.Periodicity.choices,
        initial=Action.Periodicity.EVERY_DAY,
        widget=forms.Select(),
        required=True,
        label="Периодичность",
        help_text="Выберите тип периодичности из списка"
    )
    interval = forms.IntegerField(
        widget=forms.NumberInput(),
        min_value=1,
        required=False,
        label="Интервал",
        help_text="Введите интервал дней N (только для периодичности \"Каждые N дней\")"
    )
    description = forms.CharField(
        widget=forms.Textarea(),
        required=False,
        label="Инструкция",
        help_text="Введите инструкцию"
    )

class PlantingForm(forms.Form):
    plant = forms.ModelChoiceField(
        queryset=Plant.objects.all(),
        widget=forms.Select(),
        required=True,
        label="Растение",
        help_text="Выберите растение"
    )
    location = forms.ModelChoiceField(
        queryset=Location.objects.all(),
        widget=forms.Select(),
        required=True,
        label="Локация",
        help_text="Выберите локацию"
    )