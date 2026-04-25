import os
from django.db import IntegrityError
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout, get_user
from django.contrib.auth.forms import AuthenticationForm
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from celery.result import AsyncResult
from dotenv import load_dotenv
from .forms import UserGHForm
from .models import UserGH
from apps.monitoring.models import Accident
from apps.todolist.models import Task


OBJECTS_PER_PAGE = 14


@login_required
def guide(request):
    load_dotenv()
    HA_exists = not os.getenv("HOMEASSISTANT_EXISTS", False) in [False, "False"]
    return render(request, "users/guide.html", {"HA_exists": HA_exists})


def login_user(request):
    if request.method == "POST":
        user = authenticate(username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, "users/login.html",
                          { 'form': AuthenticationForm(), 'message': 'Неверное имя пользователя или пароль.'})
        else:
            login(request, user)
            user.is_active = True
            return redirect('/todolist/')
    else:
        return render(request, "users/login.html", { 'form': AuthenticationForm() })


@login_required
def logout_user(request):
    if request.method == "POST":
        user = get_user(request)
        user.is_active = False
        logout(request)
        return redirect('/login')


@login_required
def add_user(request):
    if request.method == 'POST':
        userform = UserGHForm(request.POST)
        if userform.is_valid():
            data = userform.cleaned_data

            user = UserGH(
                username=data['username'],
                email=data['email'],
                surname=data['surname'],
                name=data['name'],
                patronymic=data['patronymic'],
                post=data['post'],
                is_active=False,
            )

            phone = data['phone']
            if len(phone) == 11 and phone[0] == '8':
                phone = "+7" + phone[1:]
            user.phone = phone

            if data['password1'] == data['password2']:
                user.set_password(data['password1'])
            else:
                return render(request, "users/add_user.html",
                              {"form": userform, "message": "Пароли не совпадают."})
            user.is_superuser = False
            user.is_staff = True

            try:
                user.save()
                # login(request, user)
                # return redirect("todolist/")
                return render(request, "users/add_user.html",
                              {"form": userform, "message": "Успещное добавление пользователя!"})
            except IntegrityError:
                return render(request, "users/add_user.html",
                              {"form": userform, "message": "Такой пользователь уже существует."})
            except Exception as e:
                return render(request, "users/add_user.html",
                              {"form": userform, "message": f"Ошибка: {e}"})
        else:
            return render(request, "users/add_user.html",
                          {"form": UserGHForm(), "message": "Форма невалидная, попробуйте ещё раз."})
    else:
        userform = UserGHForm()
        return render(request, "users/add_user.html", {"form": userform})


@login_required
def users_list(request):
    users = UserGH.objects.all().order_by('id')
    page_num = request.GET.get("page", 1)
    paginator = Paginator(users, OBJECTS_PER_PAGE)
    page_obj = paginator.get_page(page_num)
    return render(request, "users/users_list.html",
                  { "page_obj": page_obj, "count": len(users) })


@login_required
def user_detail(request, id):
    user = get_object_or_404(UserGH, pk=id)
    return render(request, "users/user.html", {"user": user})


def task_status(request, task_id):
    task = AsyncResult(task_id)

    if task.state == 'PENDING':
        return JsonResponse({"status": "PENDING"})
    elif task.state == 'STARTED':
        return JsonResponse({"status": "STARTED"})
    elif task.state == 'SUCCESS':
        return JsonResponse({"status": "SUCCESS"})
    elif task.state == 'FAILURE':
        error_msg = str(task.info) if task.info else "Неизвестная ошибка"
        return JsonResponse({"status": "FAILURE", "error": error_msg})
    else:
        return JsonResponse({"status": task.state})


@login_required
def user_stats(request, id):
    load_dotenv()

    user = get_object_or_404(UserGH, pk=id)

    tasks = Task.objects.filter(executor=user).order_by('-date', 'task_id')
    tasks_page_num = request.GET.get("tasks_page", 1)
    tasks_paginator = Paginator(tasks, 10)
    tasks_page_obj = tasks_paginator.get_page(tasks_page_num)

    accidents = Accident.objects.filter(solution__user=user).order_by('-data_from_sensors__datetime')
    accidents_page_num = request.GET.get("accidents_page", 1)
    accidents_paginator = Paginator(accidents, 10)
    accidents_page_obj = accidents_paginator.get_page(accidents_page_num)
    return render(
        request,
        "users/user_stats.html",
        {
            "user": user,
            "tasks": tasks_page_obj,
            "tasks_count": len(tasks),
            "accidents": accidents_page_obj,
            "accidents_count": len(accidents),
            "HA_exists": not os.getenv("HOMEASSISTANT_EXISTS", False) in [False, "False"],
        }
    )


@login_required
def delete_user(request, id):
    if request.method == 'POST':
        try:
            user = get_object_or_404(UserGH, pk=id)
            user.delete()
        except Exception as e:
            return JsonResponse({"success": False, "error": f"Ошибка: {e}"}, status=404)
        else:
            return JsonResponse({"success": True, "redirect_url": "/users"})
    return JsonResponse({"success": False, "error": "Непредвиденная ошибка."}, status=404)


def start(request):
    return redirect("/login")