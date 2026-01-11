import json
from pathlib import Path


class _SettingsMeta(type):
    """
    Метакласс для реализации Singleton
    """
    _instance = None

    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__call__(*args, **kwargs)
        return cls._instance


class SettingsLoader(metaclass=_SettingsMeta):
    def __init__(self):
        self._config = {}
        self._config_file = "pyproject.toml"
        self._custom_config_file = None
        self._load_config()

    def _load_config(self) -> None:
        default_config = {
            "data_directory": "data",
            "rates_ttl_seconds": 300,
            "default_base_currency": "USD",
            "log_directory": "logs",
            "log_level": "INFO",
            "log_format": "text",
            "max_log_size_mb": 10,
            "backup_log_files": 5,
            "supported_currencies": ["USD", "EUR", "RUB", "GBP", "JPY", "BTC", "ETH"],
        }

        self._config = dict(default_config)

        # pyproject.toml -> [tool.valutatrade]
        try:
            import tomllib

            with open(self._config_file, "rb") as f:
                pyproject_data = tomllib.load(f)

            valuta_config = pyproject_data.get("tool", {}).get("valutatrade", {})
            if isinstance(valuta_config, dict):
                self._config.update(valuta_config)
        except (FileNotFoundError, ImportError, OSError):
            pass

        custom_config_path = self._custom_config_file or "config.json"
        path = Path(custom_config_path)
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    custom_config = json.load(f)
                if isinstance(custom_config, dict):
                    self._config.update(custom_config)
            except (json.JSONDecodeError, OSError):
                pass

    def get(self, key: str, default=None):
        return self._config.get(key, default)

    def set(self, key: str, value) -> None:
        self._config[key] = value

    def reload(self) -> None:
        self._load_config()

    def set_config_file(self, file_path: str) -> None:
        self._custom_config_file = file_path
        self.reload()

    @property
    def data_directory(self) -> str:
        return self.get("data_directory", "data")

    @property
    def rates_ttl_seconds(self) -> int:
        return self.get("rates_ttl_seconds", 300)

    @property
    def default_base_currency(self) -> str:
        return self.get("default_base_currency", "USD")

    @property
    def log_directory(self) -> str:
        return self.get("log_directory", "logs")

    @property
    def log_level(self) -> str:
        return self.get("log_level", "INFO")

    @property
    def log_format(self) -> str:
        return self.get("log_format", "text")

    def get_data_file_path(self, filename: str) -> str:
        return str(Path(self.data_directory) / filename)


settings = SettingsLoader()