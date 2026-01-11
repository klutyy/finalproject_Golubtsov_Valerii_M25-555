import logging
from datetime import datetime

from valutatrade_hub.parser_service.api_clients import CoinGeckoClient, ExchangeRateApiClient
from valutatrade_hub.parser_service.config import ParserConfig
from valutatrade_hub.parser_service.storage import Storage

logger = logging.getLogger("ValutaTrade.Parser")


class RatesUpdater:
    def __init__(self, config: ParserConfig):
        self.__crypto_client = CoinGeckoClient(config)
        self.__fiat_client = ExchangeRateApiClient(config)
        self.storage = Storage(config)
        self.clients = {
            "CoinGecko": self.__crypto_client,
            "ExchangeRate-API": self.__fiat_client,
        }

    def run_update(self, sources):
        logger.info("Starting rates update...")

        all_rates = {}
        all_records = []

        timestamp = datetime.now()
        timestamp_str = timestamp.isoformat(timespec="seconds")

        # приводим фильтры к тому же виду, что и source_name
        source_filters = [
            s.lower().replace("-", "").replace(" ", "")
            for s in (sources or [])
        ]

        for source_name, client in self.clients.items():
            cleaned_source_name = source_name.lower().replace("-", "").replace(" ", "")
            if source_filters and cleaned_source_name not in source_filters:
                continue

            try:
                client_rates = client.fetch_rates()
                logger.info(f"Fetching from {source_name}... OK ({len(client_rates)} rates)")
            except Exception as e:
                logger.error(f"Failed to fetch from {source_name}: {e}")
                continue

            for pair, data in client_rates.items():
                from_cur, to_cur = pair.split("_")

                record = {
                    "id": f"{from_cur}_{to_cur}_{timestamp_str}",
                    "from_currency": from_cur,
                    "to_currency": to_cur,
                    "rate": data["rate"],
                    "timestamp": timestamp_str,
                    "source": source_name,
                    "meta": data["meta"],
                }
                all_records.append(record)

                all_rates[pair] = {
                    "rate": data["rate"],
                    "updated_at": timestamp_str,
                    "source": source_name,
                }

        if all_rates:
            self.storage.append_history(all_records)
            self.storage.save_rates(all_rates)
            logger.info(f"Writing {len(all_rates)} rates to data/rates.json...")

        return len(all_rates)
