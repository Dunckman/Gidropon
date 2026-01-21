from django import forms

MAX_LOGIN_LENGTH = 100
MAX_SURNAME_LENGTH = 25
MAX_NAME_LENGTH = 25
MAX_PATRONYMIC_LENGTH = 25
MAX_PHONE_LENGTH = 15
MAX_POST_LENGTH = 35

class UserGHForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(),
        max_length=MAX_LOGIN_LENGTH,
        required=True,
        label='Логин',
        help_text='Введите уникальный логин'
    )
    email = forms.EmailField(
        widget=forms.EmailInput(),
        required=True,
        label='Электронная почта',
        help_text='Введите Вашу электронную почту'
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput,
        required=True,
        label='Пароль',
        help_text='Введите пароль'
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput,
        required=True,
        label='Подтверждение пароля',
        help_text='Повторите пароль'
    )
    surname = forms.CharField(
        widget=forms.TextInput(),
        max_length=MAX_SURNAME_LENGTH,
        required=True,
        label="Фамилия",
        help_text="Введите Вашу фамилию"
    )
    name = forms.CharField(
        widget=forms.TextInput(),
        max_length=MAX_NAME_LENGTH,
        required=True,
        label="Имя",
        help_text="Введите Ваше имя"
    )
    patronymic = forms.CharField(
        widget=forms.TextInput(),
        max_length=MAX_PATRONYMIC_LENGTH,
        required=True,
        label="Отчество",
        help_text="Введите Ваше отчество"
    )
    phone = forms.CharField(
        widget=forms.TextInput(),
        max_length=MAX_PHONE_LENGTH,
        required=True,
        label="Телефон",
        help_text="Введите Ваш телефон"
    )
    post = forms.CharField(
        widget=forms.TextInput(),
        max_length=MAX_POST_LENGTH,
        required=True,
        label="Должность",
        help_text="Введите Вашу должность"
    )