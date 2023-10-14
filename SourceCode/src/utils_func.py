import utime
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


def get_int_from_json(value_name: str, file_path: str) -> int | None:
    j_file = _get_json_file(file_path)
    try:
        if isinstance(j_file[value_name], int):
            return j_file[value_name]
        else:
            return None
    except Exception as e:
        print(f"It was not possible to find value: {value_name} in json: {json.dumps(j_file)} because: {e}")


def get_str_from_json(value_name: str, file_path: str) -> str | None:
    j_file = _get_json_file(file_path)

    try:
        if isinstance(j_file[value_name], str):
            return j_file[value_name]
        else:
            return None
    except Exception as e:
        print(f"It was not possible to find value: {value_name} in json: {json.dumps(j_file)} because: {e}")
