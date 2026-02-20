from django.db import IntegrityError
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.http import JsonResponse
from django.contrib.auth import get_user
from django.core.paginator import Paginator
from datetime import datetime
from .forms import *
from .models import *

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
                return render(request, "monitoring/add/add_dfs.html",
                              {"form": dfsform, "message": "Успешное добавление показаний датчиков!"})
            except IntegrityError:
                return render(request, "monitoring/add/add_dfs.html",
                              {"form": dfsform, "message": "Такой набор показаний с датчиков уже существует."})
        else:
            return HttpResponse("<h1>Error</h1>")
    else:
        dfsform = DataFromSensorsForm()
        return render(request, "monitoring/add/add_dfs.html", {"form": dfsform})

def add_solution(request):
    if request.method == 'POST':
        solutionform = SolutionForm(request.POST)
        if solutionform.is_valid():
            data = solutionform.cleaned_data
            solution = Solution(
                recommendation=data['recommendation'],
                arguments=data['arguments'],
            )
            if data["comment"] is not None:
                solution.comment = data["comment"]
                solution.user = get_user(request)
            try:
                solution.save()
                return render(request, "monitoring/add/add_solution.html",
                              {"form": solutionform, "message": "Успешное добавление решения!"})
            except IntegrityError:
                return render(request, "monitoring/add/add_solution.html",
                              {"form": solutionform, "message": "Такое решение уже существует."})
        else:
            return HttpResponse("<h1>Error</h1>")
    else:
        solutionform = SolutionForm()
        return render(request, "monitoring/add/add_solution.html", {"form": solutionform})

def add_accident(request):
    if request.method == 'POST':
        accidentform = AccidentForm(request.POST)
        if accidentform.is_valid():
            data = accidentform.cleaned_data
            accident = Accident(
                description=data['description'],
                status=Accident.Status.NOT_ELIMINATED,
                # embedding=,
                data_from_sensors=data['data_from_sensors'],
            )
            try:
                accident.save()
                return render(request, "monitoring/add/add_accident.html",
                              {"form": accidentform, "message": "Успешное добавление аварии!"})
            except IntegrityError:
                return render(request, "monitoring/add/add_accident.html",
                              {"form": accidentform, "message": "Такая авария уже существует."})
        else:
            return HttpResponse("<h1>Error</h1>")
    else:
        accidentform = AccidentForm()
        return render(request, "monitoring/add/add_accident.html", {"form": accidentform})

def add_full(request):
