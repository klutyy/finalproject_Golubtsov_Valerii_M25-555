import json
from datetime import datetime

from valutatrade_hub.parser_service.config import ParserConfig
from valutatrade_hub.parser_service.updater import RatesUpdater

config = ParserConfig()


def from_json(filepath):
    """
    Ф-ция загружает данные из JSON-файла
    """
    try:
        with open(filepath, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def to_json(filepath, data):
    """
    Ф-ция сохраняет переданные данные в JSON-файл
    """
    with open(filepath, 'w') as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def get_rates(to_currency):
    """
    Ф-ция загружает курсы валют из JSON-файла
    """
    try:
        with open('data/rates.json', 'r') as file:
            loaded = json.load(file)

        if not isinstance(loaded, dict):
            return {}, []

        data = loaded.get('pairs', {})
        if not isinstance(data, dict):
            return {}, []

        to_currency = to_currency.upper().strip()
        last_date_str = loaded.get('last_refresh')

        if last_date_str:
            last_date = datetime.strptime(last_date_str, '%Y-%m-%dT%H:%M:%S')
            minutes = (datetime.now() - last_date).total_seconds() / 60
        else:
            minutes = 999

        if minutes > 5:
            updater = RatesUpdater(config)
            updater.run_update(None)

            with open('data/rates.json', 'r') as file:
                loaded = json.load(file)

            if not isinstance(loaded, dict):
                return {}, []

            data = loaded.get('pairs', {})
            if not isinstance(data, dict):
                return {}, []

            last_date_str = loaded.get('last_refresh')

        valid_keys = [key for key in data if key.endswith(f'_{to_currency}')]

        valid_courses = {
            key.replace(f'_{to_currency}', ''): data[key].get('rate')
            for key in valid_keys
        }

        update_dates = [last_date_str] * len(valid_courses)

        return valid_courses, update_dates

    except (FileNotFoundError, json.JSONDecodeError):
        return {}, []

