from django.http import HttpResponse
from django.shortcuts import render
from .forms import *
from .models import Plant, Location, Stage, Action, Planting

def add_plant(request):
    if request.method == 'POST':
        title = request.POST['title']
        description = request.POST['description']
        plant = Plant(
            title=title,
            description=description
        )
        plant.save()
        return HttpResponse(f"{title}<br>{description}")
    else:
        plantform = PlantForm()
        return render(request, "add_plant.html", { "form": plantform })

# def add_location(request):
#     locationform = PlantForm()
#     return render(request, "add_location.html", { "form": locationform })
#
# def add_stage(request):
#     stageform = PlantForm()
#     return render(request, "add_stage.html", { "form": stageform })
#
# def add_action(request):
#     actionform = PlantForm()
#     return render(request, "add_action.html", { "form": actionform })
#
# def add_planting(request):
#     plantingform = PlantForm()
#     return render(request, "add_planting.html", { "form": plantingform })
