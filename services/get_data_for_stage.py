from apps.todolist.models import Stage

def get_correct_order(new_stage: Stage) -> int:
    stages = Stage.objects.filter(plant_id=new_stage.plant_id).order_by('order')
    if not stages.exists():
        return 1
    return stages.last().order + 1

def get_start_finish_days(new_stage: Stage) -> tuple[int, int]:
    stages = Stage.objects.filter(plant_id=new_stage.plant_id).order_by('order')

    if not stages.exists():
        return 0, new_stage.duration - 1

    start = stages.last().finish_day + 1
    return start, start + new_stage.duration - 1