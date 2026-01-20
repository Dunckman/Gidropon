from services.get_tasks_for_today import get_tasks_for_today

class NonTasksForTodayError(Exception):
    pass

def save_cycle(tasks):
    for task in tasks:
        task.save()
    return

def save_tasks_for_today(script=True):
    tasks = get_tasks_for_today()
    if script:
        save_cycle(tasks)

    if len(tasks) == 0:
        raise NonTasksForTodayError()
    save_cycle(tasks)