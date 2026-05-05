import os
from django.db import IntegrityError
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.http import JsonResponse
from django.contrib.auth import get_user
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from celery.result import AsyncResult
from dotenv import load_dotenv
from .forms import *
from .models import *
from .tasks import check_accident
from services.llm.sensors_description import get_description, get_colors
from services.solution_parsing import generate_full_html
from services.sensors_data_logic import EmptyData
from services.llm.rag import NotAccident, NoDataForGenerate


OBJECTS_PER_PAGE = 14


@login_required
def sensor_detail(request, id):
    sensor = get_object_or_404(Sensor, pk=id)
    return render(
        request,
        "monitoring/objects/sensor.html",
        {
            "sensor": sensor,
            "normals": get_object_or_404(NormalValues, values_id=id),
        }
    )


@login_required
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


@login_required
def dfs_detail(request, id):
    dfs = get_object_or_404(DataFromSensors, pk=id)
    accident = Accident.objects.filter(data_from_sensors_id=id)
    if len(accident) == 0:
        accident = False
    else:
        accident = accident[0]
    return render(
        request,
        "monitoring/objects/dfs.html",
        {
            "dfs": dfs,
            "accident": accident,
            "colors": get_colors(dfs),
        }
    )


@login_required
def solution_detail(request, id):
    solution = get_object_or_404(Solution, pk=id)
    accident = get_object_or_404(Accident, solution_id=id)
    return render(
        request,
        "monitoring/objects/solution.html",
        {
            "solution": solution,
            "solution_html": generate_full_html(solution),
            "user": solution.user,
            "accident": accident,
        }
    )


@login_required
def accident_detail(request, id):
    accident = get_object_or_404(Accident, pk=id)
    return render(
        request,
        "monitoring/objects/accident.html",
        {
            "accident": accident,
            "solution": accident.solution,
            "solution_html": generate_full_html(accident.solution),
            "user": accident.solution.user,
            "dfs": accident.data_from_sensors,
            "colors": get_colors(accident.data_from_sensors),
        }
    )


@login_required
def add_sensor(request):
    if request.method == 'POST':
        sensorform = SensorForm(request.POST)
        if sensorform.is_valid():
            sensor = Sensor(
                parameter=sensorform.cleaned_data['title'],
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


@login_required
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


@login_required
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


@login_required
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
                solution.comment = "Авария устранена в соответствии с рекомендацией."
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


@login_required
def monitoring(request):
    load_dotenv()
    HA_exists = os.environ.get("HOMEASSISTANT_EXISTS", False)
    if HA_exists in [False, "False"]:
        return render(request, "monitoring/sad_page.html")

    accidents = Accident.objects.all().order_by('accident_id')
    not_eliminated_accidents = accidents.filter(status=Accident.Status.NOT_ELIMINATED)


    if len(not_eliminated_accidents) == 0:
        actual_accident = accidents.last()
    else:
        actual_accident = not_eliminated_accidents.last()

    page_num = request.GET.get("page", 1)
    paginator = Paginator(not_eliminated_accidents.exclude(accident_id=actual_accident.accident_id), 10)
    page_obj = paginator.get_page(page_num)

    return render(
        request,
        "monitoring/monitoring.html",
        {
            "accident": actual_accident,
            "solution": actual_accident.solution,
            "dfs": actual_accident.data_from_sensors,
            "colors": get_colors(actual_accident.data_from_sensors),
            "solution_html": generate_full_html(actual_accident.solution),
            "page_obj": page_obj,
        }
    )


@login_required
def mark_accident_done(request, id, comment):
    if request.method == 'POST':
        try:
            accident = get_object_or_404(Accident, pk=id)
            solution = get_object_or_404(Solution, pk=accident.solution_id)
        except Accident.DoesNotExist:
            return JsonResponse({"success": False, "error": "Accident does not exist."}, status=404)
        except Solution.DoesNotExist:
            return JsonResponse({"success": False, "error": "Solution does not exist."}, status=404)
        else:
            accident.status = Accident.Status.ELIMINATED
            accident.eliminated_datetime = timezone.now()
            accident.save()

            solution.user = get_user(request)
            solution.comment = comment
            solution.save()
            return JsonResponse({"success": True})
    return JsonResponse({"success": False, "error": "Invalid method"}, status=405)


@login_required
def sensors_list(request):
    sensors = Sensor.objects.all().order_by('sensor_id')
    page_num = request.GET.get("page", 1)
    paginator = Paginator(sensors, OBJECTS_PER_PAGE)
    page_obj = paginator.get_page(page_num)
    return render(request, "monitoring/lists/sensors_list.html",
                  { "page_obj": page_obj })


@login_required
def normals_list(request):
    normals = NormalValues.objects.all().order_by('sensor_id')
    page_num = request.GET.get("page", 1)
    paginator = Paginator(normals, OBJECTS_PER_PAGE)
    page_obj = paginator.get_page(page_num)
    return render(request, "monitoring/lists/normals_list.html",
                  { "page_obj": page_obj })


@login_required
def dfs_list(request):
    dfses = DataFromSensors.objects.all().order_by('-datetime')
    page_num = request.GET.get("page", 1)
    paginator = Paginator(dfses, OBJECTS_PER_PAGE)
    page_obj = paginator.get_page(page_num)
    return render(request, "monitoring/lists/dfs_list.html",
                  { "page_obj": page_obj, "count": len(dfses) })


@login_required
def solutions_list(request):
    solutions = Solution.objects.all().order_by('solution_id')
    page_num = request.GET.get("page", 1)
    paginator = Paginator(solutions, OBJECTS_PER_PAGE)
    page_obj = paginator.get_page(page_num)
    return render(request, "monitoring/lists/solutions_list.html",
                  { "page_obj": page_obj, "count": len(solutions) })


@login_required
def accidents_list(request):
    accidents = Accident.objects.all().order_by('-data_from_sensors__datetime')
    page_num = request.GET.get("page", 1)
    paginator = Paginator(accidents, OBJECTS_PER_PAGE)
    page_obj = paginator.get_page(page_num)
    return render(request, "monitoring/lists/accidents_list.html",
                  { "page_obj": page_obj, "count": len(accidents) })


@login_required
def check_new(request):
    if request.method == 'POST':
        try:
            task = check_accident.delay()
        except NoDataForGenerate:
            return JsonResponse({"success": False, "error": "На основе данных о прошлых авариях невозможно составить корректное решение новой аварии."}, status=404)
        except NotAccident:
            return JsonResponse({"success": False, "error": "Данные со всех датчиков корректны!"}, status=404)
        except EmptyData:
            return JsonResponse({"success": False, "error": "Не удалось считать данные с датчиков."}, status=404)
        except Exception as e:
            return JsonResponse({"success": False, "error": f"Ошибка: {e}"}, status=404)
        else:
            return JsonResponse({"success": True, "task_id": task.id})
    return JsonResponse({"success": False, "error": "Непредвиденная ошибка."}, status=404)


@login_required
def cancel_check_new(request, task_id):
    if request.method != 'POST':
        return JsonResponse({"success": False, "error": "Invalid method"}, status=405)

    try:
        AsyncResult(task_id).revoke(terminate=True)
    except Exception as e:
        return JsonResponse({"success": False, "error": f"Ошибка: {e}"}, status=400)

    return JsonResponse({"success": True})


@login_required
def edit_sensor(request, id):
    sensor = get_object_or_404(Sensor, pk=id)
    if request.method == "POST":
        sensorform = SensorForm(request.POST)
        if sensorform.is_valid():
            data = sensorform.cleaned_data
            for key, value in data.items():
                if key is not None and value is not None:
                    setattr(sensor, key, value)
            try:
                sensor.save()
                return redirect("/monitoring/sensors")
            except Exception as e:
                return redirect(f"/monitoring/sensor/{id}/edit")
        else:
            return redirect(f"/monitoring/sensor/{id}/edit")
    else:
        sensorform = SensorForm(initial={
            "parameter": sensor.parameter,
            "unit": sensor.unit,
            "description": sensor.description,
        })
        return render(request, "monitoring/add/add_sensor.html", {"form": sensorform, "edit": True})


@login_required
def edit_normals(request, id):
    normals = get_object_or_404(NormalValues, pk=id)
    if request.method == "POST":
        normalsform = NormalValuesForm(request.POST)
        if normalsform.is_valid():
            data = normalsform.cleaned_data
            for key, value in data.items():
                if key is not None and value is not None:
                    setattr(normals, key, value)
            try:
                normals.save()
                return redirect("/monitoring/normals")
            except Exception as e:
                return redirect(f"/monitoring/normal-values/{id}/edit")
        else:
            return redirect(f"/monitoring/normal-values/{id}/edit")
    else:
        normalsform = NormalValuesForm(initial={
            # "sensor": normals.sensor,
            "minimum": normals.minimum,
            "maximum": normals.maximum,
            "optimum": normals.optimum,
            "critical_minimum": normals.critical_minimum,
            "critical_maximum": normals.critical_maximum,
        })
        sensor = get_object_or_404(Sensor, pk=normals.sensor_id)
        return render(request, "monitoring/add/add_normals.html",
                      {"form": normalsform, "edit": True, "sensor": sensor})
