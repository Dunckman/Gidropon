from django.db import IntegrityError
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.http import JsonResponse
from django.contrib.auth import get_user
from django.core.paginator import Paginator
from datetime import datetime
from .forms import *
from .models import *
from services.llm.sensors_description import get_description
from services.solution_parsing import generate_full_html

def sensor_detail(request, id):
    sensor = get_object_or_404(Sensor, pk=id)
    return render(
        request,
        "monitoring/objects/sensor.html",
        {
            "sensor": sensor,
            "normals": get_object_or_404(NormalValues, pk=id),
        }
    )

def normals_detail(request, id):
    normals = get_object_or_404(NormalValues, pk=id)
    return render(
        request,
        "monitoring/objects/normals.html",
        {
            "normals": normals,
            "sensor": normals.sensor,
        }
    )

def dfs_detail(request, id):
    dfs = get_object_or_404(DataFromSensors, pk=id)
    return render(
        request,
        "monitoring/objects/dfs.html",
        {
            "dfs": dfs,
        }
    )

def solution_detail(request, id):
    solution = get_object_or_404(Solution, pk=id)
    return render(
        request,
        "monitoring/objects/solution.html",
        {
            "solution": solution,
            "accident": get_object_or_404(Accident, pk=id),
        }
    )

def accidents_detail(request, id):
    accident = get_object_or_404(Accident, pk=id)
    return render(
        request,
        "monitoring/objects/accident.html",
        {
            "accident": accident,
            "solution": accident.solution,
        }
    )

def add_sensor(request):
    if request.method == 'POST':
        sensorform = SensorForm(request.POST)
        if sensorform.is_valid():
            sensor = Sensor(
                parameter=sensorform.cleaned_data['title'],
                code=sensorform.cleaned_data['code'],
                unit=sensorform.cleaned_data['unit'],
                description=sensorform.cleaned_data['description'],
            )
            try:
                sensor.save()
                return render(request, "monitoring/add/add_sensor.html",
                              {"form": sensorform, "message": "Успешное добавление датчика!"})
            except IntegrityError:
                return render(request, "monitoring/add/add_sensor.html",
                              {"form": sensorform, "message": "Такой датчик уже существует."})
        else:
            return HttpResponse("<h1>Error</h1>")
    else:
        sensorform = SensorForm()
        return render(request, "monitoring/add/add_sensor.html", {"form": sensorform})

def add_normals(request):
    if request.method == 'POST':
        dfsform = NormalValuesForm(request.POST)
        if dfsform.is_valid():
            normals = NormalValues(
                sensor=dfsform.cleaned_data['sensor'],
                minimum=dfsform.cleaned_data['minimum'],
                maximum=dfsform.cleaned_data['maximum'],
                optimum=dfsform.cleaned_data['optimum'],
                critical_minimum=dfsform.cleaned_data['critical_minimum'],
                critical_maximum=dfsform.cleaned_data['critical_maximum'],
            )
            try:
                normals.save()
                return render(request, "monitoring/add/add_normals.html",
                              {"form": dfsform, "message": "Успешное добавление нормальных значений!"})
            except IntegrityError:
                return render(request, "monitoring/add/add_normals.html",
                              {"form": dfsform, "message": "Такой набор нормальных значений уже существует."})
        else:
            return HttpResponse("<h1>Error</h1>")
    else:
        dfsform = NormalValuesForm()
        return render(request, "monitoring/add/add_normals.html", {"form": dfsform})

def add_dfs(request):
    if request.method == 'POST':
        dfsform = DataFromSensorsForm(request.POST)
        if dfsform.is_valid():
            dfs = DataFromSensors(
                humidity=dfsform.cleaned_data['humidity'],
                air_temp=dfsform.cleaned_data['air_temp'],
                sol_temp=dfsform.cleaned_data['sol_temp'],
                water_level=dfsform.cleaned_data['water_level'],
                ec=dfsform.cleaned_data['ec'],
                lux=dfsform.cleaned_data['lux'],
                ph=dfsform.cleaned_data['ph'],
            )
            try:
                dfs.save()
                return redirect('/monitoring/add_solution/')
            except IntegrityError:
                return render(request, "monitoring/add/add_dfs.html",
                              {"form": dfsform, "message": "Такой набор показаний с датчиков уже существует."})
        else:
            return HttpResponse("<h1>Error</h1>")
    else:
        dfsform = DataFromSensorsForm()
        return render(request, "monitoring/add/add_dfs.html", {"form": dfsform})

def add_solution(request):
    dfs = DataFromSensors.objects.last()
    descr, flag = get_description(dfs)
    accident = Accident(
        description=descr,
        status=Accident.Status.ELIMINATED,
        eliminated_datetime=timezone.now(),
        data_from_sensors=dfs,
    )

    if request.method == 'POST':
        solutionform = SolutionForm(request.POST)
        if solutionform.is_valid():
            data = solutionform.cleaned_data
            solution = Solution(
                recommendation=data['recommendation'],
                arguments=data['arguments'],
                user=get_user(request),
            )
            if data["comment"] is not None:
                solution.comment = data["comment"]
            else:
                solution.comment = "Авария устранена в соответствии с рекомендацией"
            try:
                solution.save()
                accident.solution = solution
                accident.save()
                return redirect('/monitoring/add_dfs/')
            except IntegrityError:
                return render(request, "monitoring/add/add_solution.html",
                              {"form": solutionform, "message": "Такое решение уже существует."})
        else:
            return HttpResponse("<h1>Error</h1>")
    else:
        solutionform = SolutionForm()
        return render(request, "monitoring/add/add_solution.html", {"form": solutionform})

def monitoring(request):
    accidents = Accident.objects.all().order_by('accident_id')
    not_eliminated_accidents = accidents.filter(status=Accident.Status.NOT_ELIMINATED)

    if len(not_eliminated_accidents) == 0:
        actual_accident = accidents.last()
    else:
        actual_accident = not_eliminated_accidents.last()

    return render(
        request,
        "monitoring/monitoring.html",
        {
            "actual_accident": actual_accident,
            "solution": actual_accident.solution,
            "dfs": actual_accident.data_from_sensors,
            "solution_html": generate_full_html(actual_accident.solution),
        }
    )