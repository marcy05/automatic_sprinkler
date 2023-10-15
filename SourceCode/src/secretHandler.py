from src.utils_func import _get_json_file
from src.utils_func import _write_json_file

TELEGRAM_CONF_PATH = "src/telegram.json"

def update_telegram_pwd(telegram_pwd: str) -> bool:
    try:
        telegram_j = _get_json_file(TELEGRAM_CONF_PATH)
        telegram_j["garden_password"] = telegram_pwd
        _write_json_file(TELEGRAM_CONF_PATH, telegram_j)

    except Exception as e:
        print(f"It was not possible to write the security password file because of: {e}")


def get_telegram_pwd() -> str:
    telegram_j = _get_json_file(TELEGRAM_CONF_PATH)
    return telegram_j["garden_password"]


def set_allowed_user(user: int) -> bool:
    try:
        telegram_j = _get_json_file(TELEGRAM_CONF_PATH)
        telegram_j["allowed_users"].append(user)
        _write_json_file(TELEGRAM_CONF_PATH, telegram_j)
        return True
    except Exception:
        return False


def is_user_allowed(user: int) -> bool:
    try:
        telegram_j = _get_json_file(TELEGRAM_CONF_PATH)
        users = telegram_j["allowed_users"]

        if user in users:
            return True
        else:
            return False
    except Exception:
        return False
