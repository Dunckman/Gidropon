from celery import shared_task
from django_celery_results.models import TaskResult
from django.utils import timezone
from datetime import timedelta
from services.backups_logic import make_backup_local

@shared_task
def cleanup_old_task_results():
    days_to_keep = 7
    cutoff_date = timezone.now() - timedelta(days=days_to_keep)

    old_results = TaskResult.objects.filter(date_done__lt=cutoff_date)
    count = old_results.count()
    old_results.delete()

    return f"Удалено {count} старых результатов задач."

@shared_task
def make_backup():
    make_backup_local(is_task=True)