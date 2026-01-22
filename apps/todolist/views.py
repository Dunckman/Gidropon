from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone
from datetime import date, datetime

from .forms import *
from .models import *
from services.get_data_for_stage import get_start_finish_days, get_correct_order

def add_plant(request):
    if request.method == 'POST':
        plantform = PlantForm(request.POST)
        if plantform.is_valid():
            plant = Plant(
                title=plantform.cleaned_data['title'],
                description=plantform.cleaned_data['description'],
            )
            plant.save()
            return HttpResponse("<h1>Успешное добавление Растения в БД!</h1>")
        else:
            return HttpResponse("<h1>Error</h1>")
    else:
        plantform = PlantForm()
        return render(request, "add_plant.html", { "form": plantform })

def add_location(request):
    if request.method == 'POST':
        locationform = LocationForm(request.POST)
        if locationform.is_valid():
            location = Location(
                code=locationform.cleaned_data['code'],
                description=locationform.cleaned_data['description'],
            )
            location.save()
            return HttpResponse("<h1>Успешное добавление Локации в БД!</h1>")
        else:
            return HttpResponse("<h1>Error</h1>")
    else:
        locationform = LocationForm()
        return render(request, "add_location.html", { "form": locationform })

def add_stage(request):
    if request.method == 'POST':
        stageform = StageForm(request.POST)
        if stageform.is_valid():
            stage = Stage(
                plant=stageform.cleaned_data['plant'],
                title=stageform.cleaned_data['title'],
                duration=stageform.cleaned_data['duration'],
            )
            stage.order = get_correct_order(stage)
            sf_days = get_start_finish_days(stage)
            stage.start_day = sf_days[0]
            stage.finish_day = sf_days[1]
            stage.save()
            return HttpResponse("<h1>Успешное добавление Стадии роста в БД!</h1>")
        else:
            return HttpResponse("<h1>Error</h1>")
    else:
        stageform = StageForm()
        return render(request, "add_stage.html", { "form": stageform })

def add_action(request):
    if request.method == 'POST':
        actionform = ActionForm(request.POST)
        if actionform.is_valid():
            action = Action(
                stage=actionform.cleaned_data['stage'],
                title=actionform.cleaned_data['title'],
                periodicity=actionform.cleaned_data['periodicity'],
                interval=actionform.cleaned_data['interval'],
                instruction=actionform.cleaned_data['instruction']
            )
            if action.periodicity in ["once", "every_day"]:
                action.interval = None
            elif action.periodicity == "every_n_day" and action.interval is None:
                action.interval = 7
            action.save()
            return HttpResponse("<h1>Успешное добавление Действия в БД!</h1>")
        else:
            return HttpResponse("<h1>Error</h1>")
    else:
        actionform = ActionForm()
        return render(request, "add_action.html", { "form": actionform })

def add_planting(request):
    if request.method == 'POST':
        plantingform = PlantingForm(request.POST)
        if plantingform.is_valid():
            planting = Planting(
                plant = plantingform.cleaned_data['plant'],
                location = plantingform.cleaned_data['location'],
            )
            planting.datetime = timezone.now()
            planting.status = "growing"
            planting.save()
            return HttpResponse("<h1>Успешное добавление Посадки растения в БД!</h1>")
        else:
            return HttpResponse("<h1>Error</h1>")
    else:
        plantingform = PlantingForm()
        return render(request, "add_planting.html", { "form": plantingform })

def tasks_list(request):
    date_str = request.GET.get('date')
    if date_str:
        try:
            target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            target_date = date.today()
    else:
        target_date = date.today()

    return render(
        request,
        "tasks_list.html",
        {
            "tasks": list(Task.objects.filter(date=target_date).exclude(status="done")),
            "target_date": target_date,
        }
    )

def task_detail(request, task_id):
    task = Task.objects.get(task_id=task_id)
    return render(
        request,
        "task_detail.html",
        { "task": task, }
    )