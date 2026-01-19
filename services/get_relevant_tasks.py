import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.todolist.models import *
from django.utils import timezone
from datetime import datetime

def get_current_stage(planting: Planting, target_date: datetime):
    stages = Stage.objects.filter(plant_id=planting.plant.plant_id).order_by('order')
    if not stages.exists():
        return None

    days_delta = (target_date - planting.datetime).days
    if days_delta < 0 or days_delta > stages.last().finish_day + 1:
        return None

    for stage in stages:
        if stage.start_day <= days_delta < stage.finish_day:
            return stage

    return None

def get_actions(stage: Stage, days_delta: int) -> list[Action]:
    actions = Action.objects.filter(stage_id=stage.stage_id)
    result = []

    for action in actions:
        interval = action.interval

        if action.periodicity == "once" and stage.start_day == days_delta:
            result.append(action)
        elif action.periodicity == "every_day":
            result.append(action)
        elif (action.periodicity == "every_n_day" and interval is not None and
              interval != 0 and (days_delta - stage.start_day) % interval == 0):
                result.append(action)

    return result

def get_relevant_tasks() -> dict[Plant, str]:
    # custom_date = datetime(2026, 1, 16, 12, 0, 0)
    # today = timezone.make_aware(custom_date)
    today = timezone.now()

    relevant_tasks = dict()

    plantings = Planting.objects.all()
    if not plantings.exists():
        return relevant_tasks

    for planting in plantings:
        plant = planting.plant

        current_stage = get_current_stage(planting, today)
        if not current_stage:
            relevant_tasks[plant] = "Для данного растения в справочнике нет стадий, а значит нет и действий."
            continue

        days_delta = (today - planting.datetime).days
        actions = get_actions(current_stage, days_delta)

        if not actions:
            relevant_tasks[plant] = "Для данного растения в справочнике нет действий."
        else:
            relevant_tasks[plant] = actions

    return relevant_tasks

# if __name__ == '__main__':
#     print(get_relevant_tasks())