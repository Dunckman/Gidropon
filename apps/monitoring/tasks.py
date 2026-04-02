from celery import shared_task
from services.llm.rag import check_data, NotAccident, NoDataForGenerate
from services.get_sensors_data import save_current_data, EmptyData

@shared_task
def check_accident():
    try:
        _ = check_data(save_current_data())
    except NoDataForGenerate:
        print(
            "На основе базы данных о прошлых авариях невозможно создать корректное решение текущей аварии. " +
            "Пожалуйста внесите данные о прошлых авариях вручную."
        )
    except EmptyData:
        print("Получены пустые данные.")
    except Exception as e:
        print(f"Ошибка: {e}.")

@shared_task
def check_accident_return():
    return check_data(save_current_data())