import json
import os
import tempfile
from datetime import datetime

from valutatrade_hub.parser_service.config import ParserConfig


class Storage:
    def __init__(self, config: ParserConfig):
        self.config = config
        self.rates_path = config.RATES_FILE_PATH
        self.history_path = config.HISTORY_FILE_PATH
        os.makedirs(os.path.dirname(self.rates_path), exist_ok=True)

    def save_rates(self, pairs):
        data = {
            "pairs": pairs,
            "last_refresh": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        }
        self._atomic_write(self.rates_path, data)

    def append_history(self, records):
        existing = self._load_json(self.history_path, default=[])

        if not isinstance(existing, list):
            existing = []

        if not isinstance(records, list):
            records = []

        new_ids = {r.get("id") for r in records if isinstance(r, dict) and r.get("id")}
        filtered_existing = [
            e for e in existing
            if isinstance(e, dict) and e.get("id") not in new_ids
        ]
        updated = filtered_existing + records
        self._atomic_write(self.history_path, updated)

    def _load_json(self, path: str, default):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            return default

    def _atomic_write(self, path, data):
        dir_path = os.path.dirname(path)
        os.makedirs(dir_path, exist_ok=True)

        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                delete=False,
                suffix=".json",
                dir=dir_path,
                encoding="utf-8",
            ) as tmp:
                json.dump(data, tmp, indent=4, ensure_ascii=False, default=str)
                tmp_path = tmp.name

            os.replace(tmp_path, path)
        finally:
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except OSError:
                    pass
