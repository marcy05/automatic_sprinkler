import utime
import time
import json


def _write_json_file(file_path: str, file_content: dict):
    try:
        if len(file_content) > 0:
            utime.sleep(.1)
            fw = open(file_path, 'w')
            fw.write(json.dumps(file_content))
            fw.flush()
            fw.close()
            utime.sleep(.1)
        else:
            print("The content will not be written due to empty value")
    except Exception as e:
        print(f"Impossible to write file {file_path} because: {e}")


def _get_json_file(file_path: str) -> dict:
    try:
        utime.sleep(.1)
        f = open(file_path, 'r')
        file_json = json.load(f)
        f.close()
        utime.sleep(1)
        return dict(file_json)
    except Exception as e:
        print(f"Impossible to open the JSON file: {file_path} because: {e}")


def str2bool(variable: str) -> bool:
    if variable.lower() == "true":
        return True
    else:
        return False


def status2bool(variable: str) -> bool:
    true_list = ["on", "true"]
    if variable.lower() in true_list:
        return True
    else:
        return False


def bool2onoff(variable: bool) -> str:
    if variable:
        return "on"
    else:
        return "off"


def forced_exit_txt(text=""):
    f = open("forced_exit_event.txt", "w")
    f.write(text)
    f.close()


def get_time() -> str:
    _current_time = time.localtime()
    _year = _current_time[0]
    _month = _current_time[1]
    _day = _current_time[2]
    _hour = _current_time[3]
    _min = _current_time[4]
    _sec = _current_time[5]
    time_str = f"{_day:02}/{_month:02}/{_year} {_hour:02}:{_min:02}:{_sec:02}"
    return time_str
