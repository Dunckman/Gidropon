from django.db import IntegrityError
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.http import JsonResponse
from django.contrib.auth import get_user
from datetime import datetime
from .forms import *
from .models import *
from services.get_data_for_stage import get_start_finish_days, get_correct_order
from services.update_tasks import save_new_tasks

def add_plant(request):
    if request.method == 'POST':
        plantform = PlantForm(request.POST)
        if plantform.is_valid():
            plant = Plant(
                title=plantform.cleaned_data['title'],
                description=plantform.cleaned_data['description'],
            )
            try:
                plant.save()
                return HttpResponse("<h1>Успешное добавление Растения в БД!</h1>")
            except IntegrityError:
                return render(request, "todolist/add_plant.html",
                              {"form": plantform, "error": "Такое растение уже существует."})
        else:
            return HttpResponse("<h1>Error</h1>")
    else:
        plantform = PlantForm()
        return render(request, "todolist/add_plant.html", {"form": plantform})

def add_location(request):
    if request.method == 'POST':
        locationform = LocationForm(request.POST)
        if locationform.is_valid():
            location = Location(
                code=locationform.cleaned_data['code'],
                description=locationform.cleaned_data['description'],
            )
            try:
                location.save()
                return HttpResponse("<h1>Успешное добавление Расположения в БД!</h1>")
            except IntegrityError:
                return render(request, "todolist/add_location.html",
                              {"form": locationform, "error": "Такое расположение уже существует."})
        else:
            return HttpResponse("<h1>Error</h1>")
    else:
        locationform = LocationForm()
        return render(request, "todolist/add_location.html", {"form": locationform})

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

            try:
                stage.save()
                return HttpResponse("<h1>Успешное добавление Стадии роста в БД!</h1>")
            except IntegrityError:
                return render(request, "todolist/add_stage.html",
                              {"form": stageform, "error": "Такая стадия роста уже существует."})
            except ValidationError:
                return render(request, "todolist/add_stage.html",
                              {"form": stageform, "error": "Такая стадия роста уже существует."})
        else:
            return HttpResponse("<h1>Error</h1>")
    else:
        stageform = StageForm()
        return render(request, "todolist/add_stage.html", {"form": stageform})

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
            if action.periodicity in [Action.Periodicity.ONCE, Action.Periodicity.EVERY_DAY]:
                action.interval = None
            elif action.periodicity == Action.Periodicity.EVERY_N_DAY and action.interval is None:
                action.interval = 7
            try:
                action.save()
                return HttpResponse("<h1>Успешное добавление Действия в БД!</h1>")
            except IntegrityError:
                return render(request, "todolist/add_action.html",
                              {"form": actionform, "error": "Такое действие уже существует."})
            except ValidationError:
                return render(request, "todolist/add_action.html",
                              {"form": actionform, "error": "Такое действие уже существует."})
        else:
            return HttpResponse("<h1>Error</h1>")
    else:
        actionform = ActionForm()
        return render(request, "todolist/add_action.html", {"form": actionform})

def add_planting(request):
    if request.method == 'POST':
        plantingform = PlantingForm(request.POST)
        if plantingform.is_valid():
            planting = Planting(
                plant = plantingform.cleaned_data['plant'],
                location = plantingform.cleaned_data['location'],
            )
            planting.datetime = timezone.now()
            planting.status = Planting.Status.GROWING
            try:
                planting.save()
                save_new_tasks(planting)
                return HttpResponse("<h1>Успешное добавление Посадки в БД!</h1>")
            except IntegrityError:
                return render(request, "todolist/add_planting.html", {
                    "form": plantingform, "error": "Такая посадка уже существует."})
        else:
            return HttpResponse("<h1>Error</h1>")
    else:
        plantingform = PlantingForm()
        return render(request, "todolist/add_planting.html", {"form": plantingform})

def tasks_list(request):
    date_str = request.GET.get('date')
    if date_str:
        try:
            target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            target_date = timezone.now().date()
    else:
        target_date = timezone.now().date()

    tasks = Task.objects.filter(date=target_date)

    return render(
        request,
        "todolist/tasks_list.html",
        {
            "await_tasks": tasks.exclude(status=Task.Status.DONE),
            "done_tasks": tasks.filter(status=Task.Status.DONE),
            "target_date": target_date,
        }
    )

def task_detail(request, task_id):
    task = Task.objects.get(task_id=task_id)
    return render(
        request,
        "todolist/task_detail.html",
        {
            "task": task,
            "action": task.action,
            "planting": task.planting,
        }
    )

def plant_detail(request, plant_id):
    return render(
        request,
        "todolist/plant_detail.html",
        {
            "plant": Plant.objects.get(plant_id=plant_id),
            "stages": Stage.objects.filter(plant_id=plant_id).order_by('order'),
            "plantings": Planting.objects.filter(plant_id=plant_id).order_by('datetime'),
        }
    )

def location_detail(request, location_id):
    return render(
        request,
        "todolist/location_detail.html",
        {
            "location": Location.objects.get(location_id=location_id),
            "plantings": Planting.objects.filter(location_id=location_id).order_by('datetime'),
        }
    )

def stage_detail(request, stage_id):
    stage = Stage.objects.get(stage_id=stage_id)
    return render(
        request,
        "todolist/stage_detail.html",
        {
            "stage": stage,
            "plant": stage.plant,
            "actions": Action.objects.filter(stage_id=stage_id),
        }
    )

def action_detail(request, action_id):
    action = Action.objects.get(action_id=action_id)
    return render(
        request,
        "todolist/action_detail.html",
        {
            "action": action,
            "stage": action.stage,
            "tasks": Task.objects.filter(action_id=action_id).order_by('date'),
        }
    )

def planting_detail(request, planting_id):
    planting = Planting.objects.get(planting_id=planting_id)
    return render(
        request,
        "todolist/planting_detail.html",
        {
            "planting": planting,
            "plant": planting.plant,
            "location": planting.location,
        }
    )

def mark_task_done(request, task_id):
    if request.method == "POST":
        try:
            task = Task.objects.get(task_id=task_id)
            task.status = Task.Status.DONE
            task.eliminated_datetime = timezone.now()
            task.executor = get_user(request)
            task.save()
            return JsonResponse({"success": True})
        except Task.DoesNotExist:
            return JsonResponse({"success": False, "error": "Task not found"}, status=404)
    return JsonResponse({"success": False, "error": "Invalid method"}, status=405)

def missed_tasks(request):
    tasks = Task.objects.filter(status=Task.Status.MISSED)
    return render(request, "todolist/missed_tasks.html", {"tasks": tasks, })