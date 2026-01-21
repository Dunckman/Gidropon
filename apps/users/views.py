from django.http import HttpResponse
from django.shortcuts import render
from .forms import UserGHForm
from .models import UserGH

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

            user.set_password(userform.cleaned_data['password1'])
            user.is_superuser = False
            user.is_staff = True
            user.save()
            return HttpResponse("<h1>Успешное добавление Пользователя в БД!</h1>")
        else:
            return HttpResponse("<h1>Error</h1>")
    else:
        userform = UserGHForm()
        return render(request, "add_user.html", { "form": userform })