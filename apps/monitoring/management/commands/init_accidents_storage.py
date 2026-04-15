from django.core.management.base import BaseCommand
from services.llm.rag import init_chromadb


class Command(BaseCommand):
    help = 'Инициализация векторного хранилища с данными об авариях и их решениях.'


    def handle(self, *args, **options):
        init_chromadb()