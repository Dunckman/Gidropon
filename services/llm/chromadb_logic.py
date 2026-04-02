# import os
# import django
#
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
# django.setup()
#
# import chromadb
# from pathlib import Path
# from config.settings import BASE_DIR
# from apps.monitoring.models import Accident
# from services.FOR_DELETE.test import get_embedding
#
CHROMA_DB_PATH = Path(BASE_DIR) / "vectors"
COLLECTION_NAME = "accidents"
#
# if __name__ == "__main__":
#     client = chromadb.PersistentClient(path=str(CHROMA_DB_PATH))
#     collection = client.create_collection(COLLECTION_NAME)
#
#     accidents = Accident.objects.all()
#
#     for accident in accidents:
#         accident_id = accident.accident_id
#         description = accident.description
#
#         collection.add(
#             ids=[str(accident_id)],
#             documents=[f"Описание аварии ({accident_id}):\n{description}"],
#             metadatas=[{"accident_id": accident_id}],
#             embeddings=[get_embedding(description)],
#         )