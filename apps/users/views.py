from django.db import IntegrityError
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from .forms import UserGHForm
from .models import UserGH

@login_required
def guide(request):
    return render(request, "users/guide.html")

def login_user(request):
    if request.method == "POST":
        user = authenticate(username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, "users/login.html",
                          { 'form': AuthenticationForm(), 'message': 'Неверное имя пользователя или пароль.'})
        else:
            login(request, user)
            return redirect('/todolist/')
    else:
        return render(request, "users/login.html", { 'form': AuthenticationForm() })

@login_required
def logout_user(request):
    if request.method == "POST":
        logout(request)
        return redirect('/')

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
        else:
            return HttpResponse("<h1>Error</h1>")
    else:
        userform = UserGHForm()
        return render(request, "users/add_user.html", {"form": userform})

@login_required
def users_list(request):
    users = UserGH.objects.all().order_by('id')
    page_num = request.GET.get("page", 1)
    paginator = Paginator(users, 25)
    page_obj = paginator.get_page(page_num)
    return render(request, "users/users_list.html",
                  { "page_obj": page_obj, "count": len(users) })

@login_required
def user_detail(request, id):
    user = get_object_or_404(UserGH, pk=id)
    return render(request, "users/user.html", {"user": user})