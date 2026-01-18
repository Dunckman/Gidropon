from django.http import HttpResponse
from django.shortcuts import render
from .forms import *
from .models import Plant, Location, Stage, Action, Planting

def add_plant(request):
    if request.method == 'POST':
        plantform = PlantForm(request.POST)
        if plantform.is_valid():
            plant = Plant(
                title=plantform.cleaned_data['title'],
                description=plantform.cleaned_data['description'],
            )
            plant.save()
            return None
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
            return None
        else:
            return HttpResponse("<h1>Error</h1>")
    else:
        locationform = LocationForm()
        return render(request, "add_location.html", { "form": locationform })

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
