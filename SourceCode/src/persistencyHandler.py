import json
import utime
from src.utils_func import _get_json_file
from src.utils_func import _write_json_file

persisted_timers_file = "src/timers.json"
default_value = {"P0_activation_period": 2,
                 "P1_activation_period": 2,
                 "P2_activation_period": 2,
                 "P3_activation_period": 2,
                 "P4_activation_period": 2,
                 "P5_activation_period": 2,
                 "P6_activation_period": 2,
                 "garden_watering_iteration": 3,
                 "garden_water_iteration_delay": 10}


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
        print("It was not possible to write the default value for Pump activation period!")


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


def write_new_timer(timer_name: str, value) -> None:
    try:
        persistency = _get_json_file_extended(persisted_timers_file)
        persistency[timer_name] = value
        _write_json_file(persisted_timers_file, persistency)

    except Exception as e:
        print(
            f"It was not possible to write the value: {value}, type: {type(value)} for timer: {timer_name} or the persistency because: {e}")
        raise


def get_int_from_json(value_name: str, file_path: str) -> int | None:
    j_file = _get_json_file(file_path)
    try:
        if isinstance(j_file[value_name], int):
            return j_file[value_name]
        else:
            return None
    except Exception as e:
        print(f"It was not possible to find value: {value_name} in json: {json.dumps(j_file)} because: {e}")
