import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

import chromadb
import json
import ollama
from pathlib import Path
from config.settings import BASE_DIR
from apps.monitoring.models import Accident, DataFromSensors, Solution
from services.llm.sensors_description import get_description


CHAT_MODEL = "qwen3:14b"
EMBEDDINGS_MODEL = "nomic-embed-text:latest"
CHROMA_DB_PATH = Path(BASE_DIR) / "vectors"
COLLECTION_NAME = "accidents"
CONTEXT_SIZES_TO_TRY = [10, 10, 10, 15, 15, 15, 20, 20, 20, 25, 25, 25]


SYSTEM_MESSAGE = """
Ты — старший помощник-консультант мастера промышленной теплицы.
Твоя задача — на основе описания новой аварии и контекста из прошлых аварий, сгенерировать решение для ликвидации.

# ОБЯЗАТЕЛЬНЫЕ ПРАВИЛА:
1.  Всегда отвечай ИСКЛЮЧИТЕЛЬНО в формате валидного JSON. Никакого текста до или после JSON-объекта.
2.  В ответ включай рекомендации и аргументы ТОЛЬКО для текущих нарушений из <input>
3.  Используй ТОЛЬКО информацию из предоставленного <context>. Не придумывай ничего от себя.
4.  Если контекст не позволяет составить решение, верни `{"error": "NO_MATCHES"}`.

# ФОРМАТ ОТВЕТА (JSON):
{{
  "recommendation": [
    "Текст рекомендации 1",
    "Текст рекомендации 2"
  ],
  "arguments": [
    ["Аргумент 1 для рекомендации 1", "Аргумент 2 для рекомендации 1"],
    ["Аргумент 1 для рекомендации 2", "Аргумент 2 для рекомендации 2"]
  ]
}}
- Если рекомендация всего одна, `recommendation` будет списком из одного элемента, а `arguments` — списком, содержащим один список аргументов.
- Количество элементов в `recommendation` и `arguments` должно совпадать.
"""


def get_user_message(query: str, context: str) -> str:
    return f"""
Проанализируй новую аварию и контекст, чтобы сгенерировать решение в формате JSON.

# ДАННЫЕ ДЛЯ ОБРАБОТКИ
<input>
{query}
</input>

<context>
{context}
</context>
"""


class NotAccident(Exception):
    pass


class NoDataForGenerate(Exception):
    pass


def get_embedding(text: str, model: str = EMBEDDINGS_MODEL) -> list[float]:
    """Построение эмбеддинга из описания датчиков"""
    return ollama.embeddings(model=model, prompt=text)["embedding"]


def get_similar_accidents(query: str, n_results: int):
    """Векторный поиск"""
    client = chromadb.PersistentClient(path=str(CHROMA_DB_PATH))
    collection = client.get_collection(COLLECTION_NAME)

    query_embedding = get_embedding(query)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )
    return results['metadatas'][0] if results['metadatas'] else []


def format_context(similar_accidents: list[dict]) -> str:
    """Форматирование контекста для промпта"""
    if not similar_accidents:
        return "В базе данных нет ни одной похожей аварии."

    context_parts = []
    for acc in similar_accidents:
        description = acc.get('description', 'Нет описания')
        recommendation = acc.get('recommendation', 'Нет рекомендации')
        arguments = acc.get('arguments', 'Нет аргументов')
        context_parts.append(
            f"Описание прошлой аварии:\n{description}\n\n"
            f"Решение:\n{recommendation}\n\n"
            f"Аргументы:\n{arguments}\n\n"
        )
    return "---\n".join(context_parts)


def get_llm_response(user_message: str) -> dict:
    """Отправка запроса к LLM и получение ответа в формате JSON"""
    try:
        response = ollama.chat(
            model=CHAT_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_MESSAGE},
                {"role": "user", "content": user_message}
            ],
            format='json',
            options={"temperature": 0.1, "top_p": 0.9, "seed": 42}
        )
        content = response['message']['content']
        if not content:
            return {"error": "LLM_EMPTY_RESPONSE"}
        return json.loads(content)
    except Exception as e:
        print(f"Ошибка при вызове LLM или парсинге ответа: {e}")
        return {"error": "LLM_GENERATION_FAILED"}


def check_data(dfs: DataFromSensors) -> tuple[Accident, Solution]:
    """
    Основная функция: проверка данных, поиск имеющегося решения или генерация нового
    """
    description = get_description(dfs)

    if not description:
        raise NotAccident

    accident = Accident(
        data_from_sensors=dfs,
        description=description,
        status=Accident.Status.NEW
    )

    # проверка на существование такой же аварии раньше - тогда возвращаем её же решение без повторной генерации
    try:
        past_accident = Accident.objects.get(description=description)
        solution = Solution(
            recommendation=past_accident.solution.recommendation,
            arguments=past_accident.solution.arguments,
        )
        accident.solution = solution
        accident.status = Accident.Status.NOT_ELIMINATED

        solution.save()
        accident.save()
        add_accident_to_chroma(accident)

        return accident, solution
    except Exception:
        pass

    # итеративная генерация нового решения с разным контекстом
    json_response = None
    for size in CONTEXT_SIZES_TO_TRY:
        print(f"Попытка генерации с размером контекста: {size}...")
        similar_accidents = get_similar_accidents(description, n_results=size)
        if not similar_accidents:
            continue

        context = format_context(similar_accidents)
        user_message = get_user_message(description, context)

        current_response = get_llm_response(user_message)

        # проверка на успех: нет ключа 'error' и есть ключ 'recommendation'
        if "error" not in current_response and "recommendation" in current_response and current_response[
            "recommendation"]:
            json_response = current_response
            print(f"Успешная генерация с контекстом размера {size}!")
            break

    # обработка результата после цикла
    if not json_response:
        raise NoDataForGenerate("Не удалось сгенерировать решение после нескольких попыток с разным контекстом.")

    # извлечение данных и форматирование для БД
    recommendations_list = json_response.get('recommendation', [])
    arguments_list_of_lists = json_response.get('arguments', [])
    rec_text, arg_text = format_data_for_db(recommendations_list, arguments_list_of_lists)

    # сохранение в бд
    solution = Solution.objects.create(
        recommendation=rec_text,
        arguments=arg_text
    )
    accident = Accident.objects.create(
        data_from_sensors=dfs,
        description=description,
        solution=solution,
        status=Accident.Status.NOT_ELIMINATED
    )
    add_accident_to_chroma(accident)

    return accident, solution


def format_data_for_db(recommendations: list, arguments: list) -> tuple[str, str]:
    """Форматирование списков рекомендаций и аргументов в текстовые блоки для БД"""
    rec_str = ""
    if len(recommendations) == 1:
        rec_str = recommendations[0]
    else:
        rec_str = "\n".join(f"{i + 1}) {rec}" for i, rec in enumerate(recommendations))

    arg_str = ""
    if len(recommendations) == 1 and arguments:
        arg_str = "\n".join(f"- {arg}" for arg in arguments[0])
    else:
        parts = []
        for i, args_list in enumerate(arguments):
            args_for_rec = "\n".join(f"- {arg}" for arg in args_list)
            if len(recommendations) > 1:
                parts.append(f"Для рекомендации №{i + 1}:\n{args_for_rec}")
            else:
                parts.append(args_for_rec)
        arg_str = "\n\n".join(parts)

    return rec_str, arg_str


def add_accident_to_chroma(accident: Accident):
    """Сохранение аварии и решения в векторную БД"""
    client = chromadb.PersistentClient(path=str(CHROMA_DB_PATH))
    collection = client.get_collection(COLLECTION_NAME)
    solution = accident.solution
    collection.add(
        ids=[str(accident.accident_id)],
        documents=[f"Описание аварии: {accident.description}"],
        metadatas=[{
            "accident_id": accident.accident_id,
            "description": accident.description,
            "recommendation": solution.recommendation,
            "arguments": solution.arguments,
        }],
        embeddings=[get_embedding(accident.description)]
    )


def init_chromadb():
    """Инициализация векторной БД при первом запуске проекта"""
    client = chromadb.PersistentClient(path=str(CHROMA_DB_PATH))
    try:
        client.delete_collection(name=COLLECTION_NAME)
        print(f"Коллекция '{COLLECTION_NAME}' успешно удалена.")
    except Exception as e:
        print(f"Не удалось удалить коллекцию '{COLLECTION_NAME}' (возможно, ее и не было): {e}")

    collection = client.create_collection(name=COLLECTION_NAME)
    print(f"Коллекция '{COLLECTION_NAME}' создана.")

    accidents = Accident.objects.select_related('solution').filter(accident_id__lte=28)
    if not accidents:
        print("В базе данных Django нет аварий для добавления в ChromaDB.")
        return

    print(f"Начинается добавление {len(accidents)} записей в ChromaDB...")
    for accident in accidents:
        if accident.solution:
            add_accident_to_chroma(accident)
    print("Заполнение ChromaDB завершено.")


if __name__ == "__main__":
    print("Запуск инициализации ChromaDB...")
    init_chromadb()