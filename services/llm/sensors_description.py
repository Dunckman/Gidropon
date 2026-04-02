from django.forms.models import model_to_dict
from apps.monitoring.models import NormalValues

SENSORS = {
    "humidity": "Влажность воздуха",
    "air_temp": "Температура воздуха",
    "sol_temp": "Температура раствора",
    "water_level": "Уровень раствора в баке",
    "ec": "EC",
    "lux": "Lux",
    "ph": "pH"
}
SENSORS_IDS = {
    "humidity": 1,
    "air_temp": 2,
    "sol_temp": 3,
    "water_level": 4,
    "ec": 5,
    "lux": 6,
    "ph": 7
}

def get_description(sensors_data):
    descriptions = []
    sd_dict = model_to_dict(sensors_data)
    full_normals = NormalValues.objects.all()

    for sensor in sd_dict.keys():
        if sensor in ["data_id", "datetime"]:
            continue
        # if sensor == "lux":
        #     continue

        normals = full_normals.get(sensor_id=SENSORS_IDS[sensor])
        value = sd_dict[sensor]

        if normals.minimum <= value <= normals.maximum:
            continue
        elif value < normals.critical_minimum:
            descriptions.append(f"{SENSORS[sensor]} КРИТИЧЕСКИ НИЖЕ НОРМЫ.")
        elif value > normals.critical_maximum:
            descriptions.append(f"{SENSORS[sensor]} КРИТИЧЕСКИ ВЫШЕ НОРМЫ.")
        elif value <= normals.minimum:
            descriptions.append(f"{SENSORS[sensor]} НИЖЕ НОРМЫ.")
        else:
            descriptions.append(f"{SENSORS[sensor]} ВЫШЕ НОРМЫ.")

    return '\n'.join(descriptions)

def get_colors(sensors_data):
    colors_dict = {}
    sd_dict = model_to_dict(sensors_data)
    full_normals = NormalValues.objects.all()

    for sensor in sd_dict.keys():
        if sensor in ["data_id", "datetime"]:
            continue
        # if sensor == "lux":
        #     continue

        normals = full_normals.get(sensor_id=SENSORS_IDS[sensor])
        value = sd_dict[sensor]

        if normals.minimum <= value <= normals.maximum:
            colors_dict[sensor] = "normal"
        elif value < normals.critical_minimum:
            colors_dict[sensor] = "critical_minimum"
        elif value > normals.critical_maximum:
            colors_dict[sensor] = "critical_maximum"
        elif value <= normals.minimum:
            colors_dict[sensor] = "minimum"
        else:
            colors_dict[sensor] = "maximum"

    return colors_dict