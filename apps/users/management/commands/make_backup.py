from django.core.management.base import BaseCommand
from services.backups_logic import make_backup

class Command(BaseCommand):
    help = 'Создание backup\'а БД.'

    def handle(self, *args, **options):
        make_backup()