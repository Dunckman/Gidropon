from django.utils import timezone
from django.db.utils import IntegrityError
from apps.todolist.models import Task, Stage, Action
from .tasks_logic import get_current_stage, get_actions

def save_new_tasks(planting):
    today = timezone.now().date()
    days_delta = (today - planting.datetime.date()).days
    stage = get_current_stage(
        planting,
        days_delta,
        Stage.objects.filter(plant_id=planting.plant_id).order_by('order')
    )
    if not stage:
        return

    relevant_actions = get_actions(
        stage,
        days_delta,
        Action.objects.filter(stage_id=stage.stage_id)
    )
    if len(relevant_actions) == 0:
        return

    for action in relevant_actions:
        task = Task(
            planting=planting,
            action=action,
            date=today,
            status=Task.Status.AWAIT,
        )

        try:
            task.save()
        except IntegrityError:
            pass