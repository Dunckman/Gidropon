from django.db import IntegrityError
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.http import JsonResponse
from django.contrib.auth import get_user
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from datetime import datetime
from .forms import *
from .models import *
from .tasks import save_tasks_for_today
from services.stage_data_logic import get_start_finish_days, get_correct_order
from services.update_tasks import save_new_tasks


@login_required
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
                return render(request, "todolist/add/add_plant.html",
                              {"form": plantform, "message": "Успешное добавление растения!"})
            except IntegrityError:
                return render(request, "todolist/add/add_plant.html",
                              {"form": plantform, "message": "Такое растение уже существует."})
        else:
            return HttpResponse("<h1>Error</h1>")
    else:
        plantform = PlantForm()
        return render(request, "todolist/add/add_plant.html", {"form": plantform})


@login_required
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
                return render(request, "todolist/add/add_location.html",
                              {"form": locationform, "message": "Успешное добавление расположения!"})
            except IntegrityError:
                return render(request, "todolist/add/add_location.html",
                              {"form": locationform, "message": "Такое расположение уже существует."})
        else:
            return HttpResponse("<h1>Error</h1>")
    else:
        locationform = LocationForm()
        return render(request, "todolist/add/add_location.html", {"form": locationform})


@login_required
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
                return render(request, "todolist/add/add_stage.html",
                              {"form": stageform, "message": "Успешное добавление стадии роста!"})
            except IntegrityError:
                return render(request, "todolist/add/add_stage.html",
                              {"form": stageform, "message": "Такая стадия роста уже существует."})
            except ValidationError:
                return render(request, "todolist/add/add_stage.html",
                              {"form": stageform, "message": "Такая стадия роста уже существует."})
        else:
            return HttpResponse("<h1>Error</h1>")
    else:
        stageform = StageForm()
        return render(request, "todolist/add/add_stage.html", {"form": stageform})


@login_required
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
                return render(request, "todolist/add/add_action.html",
                              {"form": actionform, "message": "Успешное добавление действия!"})
            except IntegrityError:
                return render(request, "todolist/add/add_action.html",
                              {"form": actionform, "message": "Такое действие уже существует."})
            except ValidationError:
                return render(request, "todolist/add/add_action.html",
                              {"form": actionform, "message": "Такое действие уже существует."})
        else:
            return HttpResponse("<h1>Error</h1>")
    else:
        actionform = ActionForm()
        return render(request, "todolist/add/add_action.html", {"form": actionform})


@login_required
def add_planting(request):
    if request.method == 'POST':
        plantingform = PlantingForm(request.POST)
        if plantingform.is_valid():
            location = plantingform.cleaned_data['location']
            past_planting = Planting.objects.filter(location=location).order_by('datetime')
            if len(past_planting) > 0 and past_planting.last().status == Planting.Status.GROWING:
                return render(request, "todolist/add/add_planting.html",
                              {"form": plantingform, "message": "На выбранном расположении уже растёт растение."})

            planting = Planting(
                plant = plantingform.cleaned_data['plant'],
                location = location,
            )
            planting.datetime = timezone.now()
            planting.status = Planting.Status.GROWING
            try:
                planting.save()
                save_new_tasks(planting)
                return render(request, "todolist/add/add_planting.html",
                              {"form": plantingform, "message": "Успешное добавление посадки!"})
            except IntegrityError:
                return render(request, "todolist/add/add_planting.html", {
                    "form": plantingform, "message": "Такая посадка уже существует."})
        else:
            return HttpResponse("<h1>Error</h1>")
    else:
        plantingform = PlantingForm()
        return render(request, "todolist/add/add_planting.html", {"form": plantingform})


@login_required
def todolist(request):
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
        "todolist/todolist.html",
        {
            "await_tasks": tasks.exclude(status=Task.Status.DONE),
            "done_tasks": tasks.filter(status=Task.Status.DONE),
            "target_date": target_date,
        }
    )


@login_required
def task_detail(request, id):
    task = get_object_or_404(Task, pk=id)
    return render(
        request,
        "todolist/objects/task.html",
        {
            "task": task,
            "action": task.action,
            "planting": task.planting,
        }
    )


@login_required
def plant_detail(request, id):
    return render(
        request,
        "todolist/objects/plant.html",
        {
            "plant": get_object_or_404(Plant, pk=id),
            "stages": Stage.objects.filter(plant_id=id).order_by('order'),
            "plantings": Planting.objects.filter(plant_id=id).order_by('datetime'),
        }
    )


@login_required
def location_detail(request, id):
    return render(
        request,
        "todolist/objects/location.html",
        {
            "location": get_object_or_404(Location, pk=id),
            "plantings": Planting.objects.filter(location_id=id).order_by('datetime'),
        }
    )


@login_required
def stage_detail(request, id):
    stage = get_object_or_404(Stage, pk=id)
    return render(
        request,
        "todolist/objects/stage.html",
        {
            "stage": stage,
            "plant": stage.plant,
            "actions": Action.objects.filter(stage_id=id),
        }
    )


@login_required
def action_detail(request, id):
    action = get_object_or_404(Action, pk=id)
    return render(
        request,
        "todolist/objects/action.html",
        {
            "action": action,
            "stage": action.stage,
            "tasks": Task.objects.filter(action_id=id).order_by('date'),
        }
    )


@login_required
def planting_detail(request, id):
    planting = get_object_or_404(Planting, pk=id)
    return render(
        request,
        "todolist/objects/planting.html",
        {
            "planting": planting,
            "plant": planting.plant,
            "location": planting.location,
        }
    )


@login_required
def mark_task_done(request, id):
    if request.method == "POST":
        try:
            task = get_object_or_404(Task, pk=id)
            task.status = Task.Status.DONE
            task.eliminated_datetime = timezone.now()
            task.executor = get_user(request)
            task.save()
            return JsonResponse({"success": True})
        except Task.DoesNotExist:
            return JsonResponse({"success": False, "error": "Task not found"}, status=404)
    return JsonResponse({"success": False, "error": "Invalid method"}, status=405)


@login_required
def missed_tasks(request):
    tasks = Task.objects.filter(status=Task.Status.MISSED)
    return render(request, "todolist/missed_tasks.html", {"tasks": tasks, })


@login_required
def edit_plant(request, id):
    plant = get_object_or_404(Plant, pk=id)
    if request.method == "POST":
        plantform = PlantForm(request.POST)
        if plantform.is_valid():
            data = plantform.cleaned_data
            for key, value in data.items():
                if key is not None and value is not None:
                    setattr(plant, key, value)
            try:
                plant.save()
                return redirect("/todolist/plants")
            except IntegrityError:
                return render(request, "todolist/add/add_plant.html",
                              {"form": plantform, "message": "Такое растение уже существует."})
        else:
            return HttpResponse("<h1>Error</h1>")
    else:
        plantform = PlantForm(initial={
            "title": plant.title,
            "description": plant.description,
        })
        return render(request, "todolist/add/add_plant.html", {"form": plantform})


@login_required
def edit_location(request, id):
    location = get_object_or_404(Location, pk=id)
    if request.method == "POST":
        locationform = LocationForm(request.POST)
        if locationform.is_valid():
            data = locationform.cleaned_data
            for key, value in data.items():
                if key is not None and value is not None:
                    setattr(location, key, value)
            try:
                location.save()
                return redirect("/todolist/locations")
            except IntegrityError:
                return render(request, "todolist/add/add_location.html",
                              {"form": locationform, "message": "Такое расположение уже существует."})
        else:
            return HttpResponse("<h1>Error</h1>")
    else:
        locationform = LocationForm(initial={
            "code": location.code,
            "description": location.description,
        })
        return render(request, "todolist/add/add_location.html", {"form": locationform})


@login_required
def edit_stage(request, id):
    stage = get_object_or_404(Stage, pk=id)
    if request.method == 'POST':
        stageform = StageForm(request.POST)
        if stageform.is_valid():
            data = stageform.cleaned_data
            for key, value in data.items():
                if key is not None and value is not None:
                    setattr(stage, key, value)
            stage.finish_day = stage.start_day + data["duration"] - 1
            try:
                stage.save()
                return redirect("/todolist/stages")
            except IntegrityError:
                return render(request, "todolist/add/add_stage.html",
                              {"form": stageform, "message": "Такая стадия роста уже существует."})
            except ValidationError:
                return render(request, "todolist/add/add_stage.html",
                              {"form": stageform, "message": "Такая стадия роста уже существует."})
        else:
            return HttpResponse("<h1>Error</h1>")
    else:
        stageform = StageForm(initial={
            "plant": stage.plant,
            "title": stage.title,
            "duration": stage.duration,
        })
        return render(request, "todolist/add/add_stage.html", {"form": stageform})


@login_required
def edit_action(request, id):
    action = get_object_or_404(Action, pk=id)
    if request.method == "POST":
        actionform = ActionForm(request.POST)
        if actionform.is_valid():
            data = actionform.cleaned_data
            for key, value in data.items():
                if key is not None and value is not None:
                    setattr(action, key, value)
            try:
                action.save()
                return redirect("/todolist/actions")
            except IntegrityError:
                return render(request, "todolist/add/add_action.html",
                              {"form": actionform, "message": "Такое действие уже существует."})
        else:
            return HttpResponse("<h1>Error</h1>")
    else:
        actionform = ActionForm(initial={
            "stage": action.stage,
            "title": action.title,
            "periodicity": action.periodicity,
            "interval": action.interval,
            "instruction": action.instruction,
        })
        return render(request, "todolist/add/add_action.html", {"form": actionform})


@login_required
def edit_planting(request, id):
    planting = get_object_or_404(Planting, pk=id)
    if request.method == "POST":
        plantingform = PlantingForm(request.POST)
        if plantingform.is_valid():
            data = plantingform.cleaned_data
            for key, value in data.items():
                if key is not None and value is not None:
                    setattr(planting, key, value)
            try:
                planting.save()
                return redirect("/todolist/plantings")
            except IntegrityError:
                return render(request, "todolist/add/add_planting.html",
                              {"form": plantingform, "message": "Такая посадка уже существует."})
        else:
            return HttpResponse("<h1>Error</h1>")
    else:
        plantingform = PlantForm(initial={
            "plant": planting.plant,
            "location": planting.location,
        })
        return render(request, "todolist/add/add_planting.html", {"form": plantingform})


@login_required
def plants_list(request):
    plants = Plant.objects.all().order_by('title', 'plant_id')
    page_num = request.GET.get("page", 1)
    paginator = Paginator(plants, 25)
    page_obj = paginator.get_page(page_num)
    return render(request, "todolist/lists/plants_list.html",
                  { "page_obj": page_obj, "count": len(plants) })


@login_required
def locations_list(request):
    locations = Location.objects.all().order_by('code', 'location_id')
    page_num = request.GET.get("page", 1)
    paginator = Paginator(locations, 25)
    page_obj = paginator.get_page(page_num)
    return render(request, "todolist/lists/locations_list.html",
                  { "page_obj": page_obj, "count": len(locations) })


@login_required
def stages_list(request):
    stages = Stage.objects.all().order_by('plant_id', 'order')
    page_num = request.GET.get("page", 1)
    paginator = Paginator(stages, 25)
    page_obj = paginator.get_page(page_num)
    return render(request, "todolist/lists/stages_list.html",
                  { "page_obj": page_obj, "count": len(stages) })


@login_required
def actions_list(request):
    actions = Action.objects.all().order_by('stage_id', 'action_id')
    page_num = request.GET.get("page", 1)
    paginator = Paginator(actions, 25)
    page_obj = paginator.get_page(page_num)
    return render(request, "todolist/lists/actions_list.html",
                  { "page_obj": page_obj, "count": len(actions) })


@login_required
def plantings_list(request):
    plantings = Planting.objects.all().order_by('-datetime')
    page_num = request.GET.get("page", 1)
    paginator = Paginator(plantings, 25)
    page_obj = paginator.get_page(page_num)
    return render(request, "todolist/lists/plantings_list.html",
                  { "page_obj": page_obj, "count": len(plantings) })


@login_required
def tasks_list(request):
    tasks = Task.objects.all().order_by('-date', 'task_id')
    page_num = request.GET.get("page", 1)
    paginator = Paginator(tasks, 25)
    page_obj = paginator.get_page(page_num)
    return render(request, "todolist/lists/tasks_list.html",
                  { "page_obj": page_obj, "count": len(tasks) })


@login_required
def add_today_tasks(request):
    if request.method == 'POST':
        try:
            task = save_tasks_for_today.delay()
        except Exception as e:
            return JsonResponse({"success": False, "error": f"Ошибка: {e}"}, status=404)
        else:
            return JsonResponse({"success": True, "task_id": task.id})
    return JsonResponse({"success": False, "error": "Непредвиденная ошибка."}, status=404)


@login_required
def delete_plant(request, id):
    if request.method == 'POST':
        try:
            plant = get_object_or_404(Plant, pk=id)
            plant.delete()
        except Exception as e:
            return JsonResponse({"success": False, "error": f"Ошибка: {e}"}, status=404)
        else:
            return JsonResponse({"success": True, "redirect_url": "/todolist/plants"})
    return JsonResponse({"success": False, "error": "Непредвиденная ошибка."}, status=404)


@login_required
def delete_location(request, id):
    if request.method == 'POST':
        try:
            location = get_object_or_404(Location, pk=id)
            location.delete()
        except Exception as e:
            return JsonResponse({"success": False, "error": f"Ошибка: {e}"}, status=404)
        else:
            return JsonResponse({"success": True, "redirect_url": "/todolist/locations"})
    return JsonResponse({"success": False, "error": "Непредвиденная ошибка."}, status=404)


@login_required
def mark_planting_dead(request, id):
    if request.method == 'POST':
        try:
            planting = get_object_or_404(Planting, pk=id)
            planting.status = Planting.Status.DEAD
            planting.save()
        except Exception as e:
            return JsonResponse({"success": False, "error": f"Ошибка: {e}"}, status=404)
        else:
            return JsonResponse({"success": True, "redirect_url": "/todolist/plantings"})
    return JsonResponse({"success": False, "error": "Непредвиденная ошибка."}, status=404)