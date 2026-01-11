import hashlib


class User:
    """
    Класс пользователя, который содержит информацию о нем и ф-ция для работы
    """

    def __init__(self, user_id, username, password_hash, salt, registration_date) -> None:
        self._user_id = user_id
        self._username = username
        self._hashed_password = password_hash
        self._salt = salt
        self._registration_date = registration_date

    @property
    def username(self) -> str:
        return self._username

    @username.setter
    def username(self, value: str) -> None:
        if not value:
            raise ValueError("Username must be filled in")
        self._username = value

    @property
    def user_id(self) -> int:
        return self._user_id

    @user_id.setter
    def user_id(self, value: int) -> None:
        self._user_id = value

    @property
    def registration_date(self):
        return self._registration_date

    def get_user_info(self):
        """
        Ф-ция возвращает информацию о пользователе
        """
        return (
            f"Name: {self._username}\n"
            f"ID: {self._user_id}\n"
            f"Registration date: {self._registration_date}"
        )

    def _hash_password(self, password: str):
        """
        Ф-ция возвращает sha256 пароля с использованием соли
        """
        if not isinstance(password, str):
            raise TypeError("password must be a string")
        data = (password + self._salt).encode("utf-8")
        return hashlib.sha256(data).hexdigest()  # [web:11]

    def change_password(self, new_password: str) -> None:
        """
        Ф-ция меняет пароль пользователя и пересчитывает его хеш
        """
        if len(new_password) < 4:
            raise ValueError("password must be at least 4 characters long")
        self._hashed_password = self._hash_password(new_password)

    def verify_password(self, password: str) -> bool:
        """
        Ф-ция валидации пароля
        """
        if not isinstance(password, str):
            return False
        return self._hashed_password == self._hash_password(password)


class Wallet:
    """
    Класс кошелька, который содержит информацию о нем и ф-ции для работы
    """

    def __init__(self, currency_code: str):
        if not isinstance(currency_code, str) or not currency_code.strip():
            raise ValueError("currency_code cannot be empty")

        self.currency_code = currency_code.strip().upper()
        self._balance: float = 0.0

    @property
    def balance(self) -> float:
        return self._balance

    @balance.setter
    def balance(self, value: float):
        if not isinstance(value, (int, float)):
            raise ValueError("balance must be a number")
        if value < 0:
            raise ValueError("balance can't be negative")

        self._balance = float(value)

    def deposit(self, amount: float):
        """
        Ф-ция для пополнение баланса
        """
        if not isinstance(amount, (int, float)):
            raise ValueError("amount must be a number")
        if amount <= 0:
            raise ValueError("amount can't be negative")

        self._balance += float(amount)

    def withdraw(self, amount: float):
        """
        Ф-ция для снятие средств
        """
        if not isinstance(amount, (int, float)):
            raise ValueError("amount must be a number")
        if amount <= 0:
            raise ValueError("amount must be positive")
        if amount > self._balance:
            raise ValueError("insufficient funds")

        self._balance -= float(amount)

    def get_balance_info(self):
        """
        Ф-ция возвращает информацию о балансе
        """
        return {
            "currency_code": self.currency_code,
            "balance": self._balance,
        }


class Portfolio:
    """
    При покупке валюты сумма списывается с USD-кошелька.
    При продаже — сумма начисляется на USD-кошелёк.
    """

    def __init__(self, user_id, wallets):
        self._user_id = user_id
        self._wallets = wallets

    def add_currency(self, currency_code: str):
        """
        Ф-ция добавляет новый кошелёк в портфель
        """
        if not isinstance(currency_code, str) or not currency_code.strip():
            raise ValueError("currency_code cannot be empty")

        currency_code = currency_code.strip().upper()

        if currency_code in self._wallets:
            return  # по ТЗ: уникальность, просто не добавляем

        self._wallets[currency_code] = Wallet(currency_code)

    def get_total_value(self, base_currency: str = "USD"):
        """
        Ф-ция возвращает общую стоимость всех валют пользователя в base_currency
        """
        if not isinstance(base_currency, str) or not base_currency.strip():
            raise ValueError("base_currency cannot be empty")

        base_currency = base_currency.strip().upper()

        rates_to_usd = {
            "USD": 1.0,
            "EUR": 1.1,
            "BTC": 60000.0,
            "RUB": .011,
        }

        if base_currency not in rates_to_usd:
            raise ValueError(f"unsupported base_currency: {base_currency}")

        total_usd = .0
        for currency, wallet in self._wallets.items():
            if currency not in rates_to_usd:
                raise ValueError(f"missing rate for currency: {currency}")
            total_usd += wallet.balance * rates_to_usd[currency]

        return total_usd / rates_to_usd[base_currency]

    def get_wallet(self, currency_code: str):
        """
        Ф-ция возвращает wallet по коду валюты
        """
        if not isinstance(currency_code, str) or not currency_code.strip():
            return None
        return self._wallets.get(currency_code.strip().upper())

    @property
    def user(self):
        return User(self._user_id)

    @property
    def wallets(self):
        return dict(self._wallets)
