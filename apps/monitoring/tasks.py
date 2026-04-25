from celery import shared_task
from services.llm.rag import check_data, NotAccident, NoDataForGenerate
from services.sensors_data_logic import (
    save_current_data,
    EmptyData,
    HomeAssistantNotExists,
)


@shared_task
def check_accident():
    try:
        _ = check_data(save_current_data())
    except NoDataForGenerate:
        print(
            "Cannot generate a correct decision for the current accident "
            "because there is not enough historical accident data."
        )
        raise
    except EmptyData:
        print("Received empty sensor data.")
        raise
    except HomeAssistantNotExists:
        print("HomeAssistant module is not installed in your system.")
        raise
    except Exception as e:
        print(f"Error: {e}.")
        raise


@shared_task
def check_accident_return():
    return check_data(save_current_data())
