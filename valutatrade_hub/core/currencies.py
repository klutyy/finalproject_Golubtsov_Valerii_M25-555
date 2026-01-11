from abc import ABC, abstractmethod

from valutatrade_hub.core.exceptions import CurrencyNotFoundError


class Currency(ABC):
    def __init__(self, name: str, code: str) -> None:
        if not isinstance(name, str) or not name.strip():
            raise ValueError("name must be a non-empty string")

        if (
            not isinstance(code, str)
            or code != code.upper()
            or not (2 <= len(code) <= 5)
            or " " in code
        ):
            raise ValueError("code must be 2..5 uppercase chars without spaces")

        self.name = name.strip()
        self.code = code

    @abstractmethod
    def get_display_info(self) -> str:
        pass


class FiatCurrency(Currency):
    def __init__(self, name: str, code: str, issuing_country: str) -> None:
        super().__init__(name, code)
        self.issuing_country = issuing_country

    def get_display_info(self) -> str:
        return f'[FIAT] {self.code} — {self.name} (Issuing: {self.issuing_country})'


class CryptoCurrency(Currency):
    def __init__(self, name: str, code: str, algorithm: str, market_cap: str) -> None:
        super().__init__(name, code)
        self.algorithm = algorithm
        self.market_cap = market_cap

    def get_display_info(self) -> str:
        return f'[CRYPTO] {self.code} — {self.name} (Algo: {self.algorithm}, MCAP: {self.market_cap})'


class CurrencyMaker:
    def __init__(self) -> None:
        self.__currency_dict = {
            "USD": FiatCurrency("US Dollar", "USD", "United States"),
            "BTC": CryptoCurrency("Bitcoin", "BTC", "SHA-256", "1.12e12"),
            "ETH": CryptoCurrency("Ethereum", "ETH", "SHA-256", "1.12e12"),
            "SOL": CryptoCurrency("Solana", "SOL", "SHA-256", "1.12e12"),
            "EUR": FiatCurrency("Euro", "EUR", "European Union"),
            "GBP": FiatCurrency("British Pound", "GBP", "United Kingdom"),
            "RUB": FiatCurrency("Ruble", "RUB", "Russian Federation"),
        }

    def get_currency(self, code: str):
        code_upper = code.upper()
        currency = self.__currency_dict.get(code_upper)
        if currency is None:
            raise CurrencyNotFoundError(code_upper)
        return currency

    def get_currency_list(self):
        return list(self.__currency_dict.keys())
