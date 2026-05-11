import paramiko
import json
import os
from dotenv import load_dotenv
from apps.monitoring.models import DataFromSensors


class EmptyData(Exception):
    pass


class HomeAssistantNotExists(Exception):
    pass


def fetch_remote_sensor_data():
    """
    Подключается по SSH (пароль), выполняет SQL и возвращает словарь данных.
    """

    load_dotenv()
    if os.getenv("HOMEASSISTANT_EXISTS", False) in [False, "False"]:
        raise HomeAssistantNotExists

    host = os.environ.get("SSH_HOST")
    user = os.environ.get("SSH_USER")
    password = os.environ.get("SSH_PASSWORD")
    db_path = os.environ.get("HOMEASS_DB_PATH")

    # Тот самый SQL запрос (PIVOT), который мы утвердили
    # Флаг -json для sqlite3 сделает всю работу по форматированию
    sql_query = """
                SELECT datetime('now', 'localtime')                                            as log_time, \
                       MAX(CASE WHEN m.entity_id LIKE '%_lux' THEN s.state END)                as lux, \
                       MAX(CASE WHEN m.entity_id LIKE '%_temp_vozdukha' THEN s.state END)      as temp_air, \
                       MAX(CASE WHEN m.entity_id LIKE '%_temp_rastvora' THEN s.state END)      as temp_water, \
                       MAX(CASE WHEN m.entity_id LIKE '%_vlazhnost_vozdukha' THEN s.state END) as humidity, \
                       MAX(CASE WHEN m.entity_id LIKE '%_ec' THEN s.state END)                 as ec, \
                       MAX(CASE WHEN m.entity_id LIKE '%_ph' THEN s.state END)                 as ph, \
                       MAX(CASE WHEN m.entity_id LIKE '%_uroven' THEN s.state END)             as level
                FROM states s
                         JOIN states_meta m ON s.metadata_id = m.metadata_id
                WHERE s.state_id IN (SELECT MAX(state_id) \
                                     FROM states s2 \
                                              JOIN states_meta m2 ON s2.metadata_id = m2.metadata_id \
                                     WHERE m2.entity_id LIKE 'sensor.shat_agrocontrol_%' \
                                     GROUP BY s2.metadata_id); \
                """

    # Формируем команду для исполнения на сервере
    # Экранируем кавычки для bash
    remote_cmd = f'sqlite3 -json {db_path} \"{sql_query}\"'

    client = paramiko.SSHClient()

    # ВАЖНО: Автоматически добавлять ключи сервера (чтобы не спрашивал yes/no при первом входе)
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # Подключение по паролю
        client.connect(hostname=host, username=user, password=password, timeout=10)

        # Выполнение команды
        stdin, stdout, stderr = client.exec_command(remote_cmd)

        # Чтение вывода
        output = stdout.read().decode('utf-8').strip()
        error = stderr.read().decode('utf-8').strip()

        if error and not output:
            raise Exception(f"SSH Error: {error}")

        if not output:
            return None

        # Парсинг JSON
        data_list = json.loads(output)
        return data_list[0] if data_list else None

    finally:
        client.close()

def clean_value(value):
    """Конвертирует строки в float или None"""
    if value in [None, 'unavailable', 'unknown', '']:
        return None
    try:
        return float(value)
    except ValueError:
        return None

def save_current_data():
    raw_data = fetch_remote_sensor_data()

    if not raw_data:
        raise EmptyData("Не удалось получить данные с датчиков.")

    new_dfs = DataFromSensors(
        lux=clean_value(raw_data.get('lux')),
        air_temp=clean_value(raw_data.get('temp_air')),
        sol_temp=clean_value(raw_data.get('temp_water')),
        humidity=clean_value(raw_data.get('humidity')),
        ec=clean_value(raw_data.get('ec')),
        ph=clean_value(raw_data.get('ph')),
        water_level=clean_value(raw_data.get('level')),
    )

    # Если датчики недоступны и пришли только пустые значения,
    # не пытаемся писать в БД (там поля not null).
    if all(
        value is None for value in (
            new_dfs.lux,
            new_dfs.air_temp,
            new_dfs.sol_temp,
            new_dfs.humidity,
            new_dfs.ec,
            new_dfs.ph,
            new_dfs.water_level,
        )
    ):
        raise EmptyData("Датчики сейчас недоступны. Проверьте Home Assistant и повторите позже.")

    new_dfs.save()
    return new_dfs
