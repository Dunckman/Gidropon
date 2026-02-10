from django.db import IntegrityError
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from .forms import UserGHForm
from .models import UserGH

def login_user(request):
    if request.method == "POST":
        user = authenticate(username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, "users/main_page.html",
                          { 'form': AuthenticationForm(), 'error': 'Неверное имя пользователя или пароль.'})
        else:
            login(request, user)
            return redirect('/todolist/')
    else:
        return render(request, "users/login.html", { 'form': AuthenticationForm() })

def add_user(request):
    if request.method == 'POST':
        userform = UserGHForm(request.POST)
        if userform.is_valid():
            user = UserGH(
                username=userform.cleaned_data['username'],
                email=userform.cleaned_data['email'],
                surname=userform.cleaned_data['surname'],
                name=userform.cleaned_data['name'],
                patronymic=userform.cleaned_data['patronymic'],
                post=userform.cleaned_data['post'],
            )

            phone = userform.cleaned_data['phone']
            if len(phone) == 11 and phone[0] == '8':
                phone = "+7" + phone[1:]
            user.phone = phone

            if userform.cleaned_data['password1'] == userform.cleaned_data['password2']:
                user.set_password(userform.cleaned_data['password1'])
            else:
                return render(request, "users/add_user.html", {"form": userform, "error": "Пароли не совпадают."})
            user.is_superuser = False
            user.is_staff = True

            try:
                user.save()
                # login(request, user)
                # return redirect("todolist/")
                return HttpResponse("<h1>Успешное добавление Пользователя в БД!</h1>")
            except IntegrityError:
                return render(request, "users/add_user.html", {"form": userform, "error": "Такой пользователь уже существует."})
        else:
            return HttpResponse("<h1>Error</h1>")
    else:
        userform = UserGHForm()
        return render(request, "users/add_user.html", {"form": userform})