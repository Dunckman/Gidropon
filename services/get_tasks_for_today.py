from django.utils import timezone
from apps.todolist.models import *

def get_current_stage(planting, days_delta, stages):
    if days_delta < 0:
        return None
    if days_delta > stages.last().finish_day:
        planting.status = Planting.Status.COMPLETED
        planting.save()
        return None

    for stage in stages:
        if stage.start_day <= days_delta <= stage.finish_day:
            return stage
    return None

def get_actions(stage, days_delta, actions):
    relevant_actions = []
    for action in actions:
        interval = action.interval
        if action.periodicity == "every_day":
            relevant_actions.append(action)
        elif action.periodicity == "once" and stage.start_day == days_delta:
            relevant_actions.append(action)
        elif (action.periodicity == "every_n_day" and interval is not None and
              interval != 0 and (days_delta - stage.start_day) % interval == 0):
            relevant_actions.append(action)

    return relevant_actions

def get_tasks_for_today():
    today = timezone.now().date()
    today_tasks = []

    plantings_db = Planting.objects.all()
    stages_db = Stage.objects.all()
    actions_db = Action.objects.all()
    if not plantings_db.exists() or not stages_db.exists() or not actions_db.exists():
        return []

    for planting in plantings_db:
        if planting.status == "completed":
            continue

        days_delta = (today - planting.datetime.date()).days
        stage = get_current_stage(planting, days_delta, stages_db.filter(plant_id=planting.plant_id).order_by('order'))
        if not stage:
            continue

        relevant_actions = get_actions(stage, days_delta, actions_db.filter(stage_id=stage.stage_id))
        if len(relevant_actions) == 0:
            continue

        for action in relevant_actions:
            task = Task(
                planting=planting,
                action=action,
                date=today,
                status=Task.Status.AWAIT,
            )
            today_tasks.append(task)

    return today_tasks