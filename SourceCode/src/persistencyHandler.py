import json
import utime
from src.utils_func import _get_json_file
from src.utils_func import _write_json_file

persisted_timers_file = "src/timers.json"
pump_persist_file = "src/pump.json"

default_pump_active = {"p0_active": True,
                       "p1_active": True,
                       "p2_active": True,
                       "p3_active": True,
                       "p4_active": True,
                       "p5_active": True,
                       "p6_active": True}

default_value = {"P0_activation_period": 2,
                 "P1_activation_period": 2,
                 "P2_activation_period": 2,
                 "P3_activation_period": 2,
                 "P4_activation_period": 2,
                 "P5_activation_period": 2,
                 "P6_activation_period": 2,
                 "garden_watering_iteration": 3,
                 "garden_water_iteration_delay": 10,
                 "backend_sync_period": 10,
                 "sensor_reading_period": 10}


def _write_default_value():
    print("Writing default value for pump activation!")
    try:
        utime.sleep(.1)
        fw = open(persisted_timers_file, 'w')
        fw.write(json.dumps(default_value))
        fw.flush()
        fw.close()
        utime.sleep(.1)
    except Exception as e:
        print("It was not possible to write the default value for Pump activation period! Reason: {e}")


def _get_json_file_extended(file_path: str) -> dict:
    try:
        file_content_json = _get_json_file(file_path)
        return file_content_json
    except Exception as e:
        print(f"Impossible to open the JSON file: {file_path} because: {e}")
        print("Writing default value...")
        _write_default_value()
        print("Default value written.")
        print("Returning default values")
        return default_value


def get_persisted_timers(timer_name: str):
    """
        arg:
            timer_name -> name of the timer that will be search in the persistency file

        return:
            It returns the value of the json or None
    """
    timers = _get_json_file_extended(persisted_timers_file)
    try:
        return timers[timer_name]
    except Exception as e:
        print(f"Not possible to find the key: {timer_name} in persistence: {timers}")


def write_persistency_value(persistency_name: str, value) -> None:
    try:
        persistency = _get_json_file_extended(persisted_timers_file)
        persistency[persistency_name] = value
        _write_json_file(persisted_timers_file, persistency)

    except Exception as e:
        print(
            f"It was not possible to write the value: {value}, type: {type(value)} for timer: {persistency_name} or the persistency because: {e}")
        raise


def get_int_from_json(value_name: str, file_path: str) -> int | None:
    j_file = _get_json_file_extended(file_path)
    try:
        if isinstance(j_file[value_name], int):
            return j_file[value_name]
        else:
            return None
    except Exception as e:
        print(f"It was not possible to find value: {value_name} in json: {json.dumps(j_file)} because: {e}")


def get_float_from_json(value_name: str, file_path: str) -> float | None:
    j_file = _get_json_file_extended(file_path)
    try:
        if isinstance(j_file[value_name], float):
            return j_file[value_name]
        else:
            return None
    except Exception as e:
        print(f"It was not possible to find value: {value_name} in json: {json.dumps(j_file)} because: {e}")


def _write_pump_default():
    print("Writing default value for pump active status!")
    try:
        utime.sleep(.1)
        fw = open(pump_persist_file, 'w')
        fw.write(json.dumps(default_pump_active))
        fw.flush()
        fw.close()
        utime.sleep(.1)
    except Exception as e:
        print(f"It was not possible to write the default value for Pump activation period! Reason: {e}")


def _get_json_pump_extended(file_path: str) -> dict:
    try:
        file_content_json = _get_json_file(file_path)
        return file_content_json
    except Exception as e:
        print(f"Impossible to open the Pump JSON file: {file_path} because: {e}")
        print("Writing default value...")
        _write_pump_default()
        print("Default value written.")
        print("Returning default values")
        return default_value


def get_pump_active_status(pump_id: int) -> bool:
    j_file = _get_json_pump_extended(pump_persist_file)
    key = f"p{pump_id}_active"

    try:
        return j_file[key]
    except Exception as e:
        print(f"It was not possible to find an entry for key: {key} in json: {j_file} because: {e}")


def write_pump_active_staus(pump_id: int, value: bool) -> None:
    j_file = _get_json_pump_extended(pump_persist_file)

    key = f"p{pump_id}_active"
    try:
        j_file[key] = value
        _write_json_file(pump_persist_file, j_file)

    except Exception as e:
        print(f"Ita was not possible to write the pump persistency file because of: {e}")
        raise
