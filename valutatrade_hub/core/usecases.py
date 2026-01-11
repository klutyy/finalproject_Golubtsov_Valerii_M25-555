import hashlib
import random
from datetime import datetime

from prettytable import PrettyTable

from valutatrade_hub.core.currencies import CurrencyMaker
from valutatrade_hub.core.exceptions import CurrencyNotFoundError, InsufficientFundsError
from valutatrade_hub.core.utils import from_json, get_rates, to_json
from valutatrade_hub.decorators import log_action
from valutatrade_hub.parser_service.config import ParserConfig
from valutatrade_hub.parser_service.updater import RatesUpdater

config = ParserConfig()

def register(username, password):
    data = from_json('data/users.json') or []

    names = [user.get('username') for user in data]
    id = [user.get('user_id') for user in data if user.get('user_id') is not None]

    if username in names:
        print(f'Имя пользователя {username} уже занято')
        return None

    if len(password) < 4:
        print('Пароль должен быть не короче 4 символов')
        return None

    current_id = max(id) + 1 if id else 1

    symbols = '1234567890-=+*%!?><$#@;:qwertyuiopasdfghjklzxcvbnm'
    salt = ''.join(random.choices(symbols, k=random.randint(5, 20)))
    hashed_password = hashlib.sha256(
        (password + salt).encode('utf-8')
    ).hexdigest()

    new_user = {
        "user_id": current_id,
        "username": username,
        "hashed_password": hashed_password,
        "salt": salt,
        "registration_date": str(datetime.now()),
    }

    data.append(new_user)
    to_json('data/users.json', data)

    portfolios = from_json('data/portfolios.json') or []
    portfolios.append({"user_id": current_id, "wallets": {}})
    to_json('data/portfolios.json', portfolios)

    return current_id

def login(username, password):
    data = from_json('data/users.json') or []

    user = next(
        (val for val in data if val.get('username') == username),
        None
    )

    if user is None:
        print(f'Пользователь {username} не найден')
        return None

    salt = user.get('salt')
    hashed_password = user.get('hashed_password')
    user_id = user.get('user_id')

    check_hash = hashlib.sha256(
        (password + salt).encode('utf-8')
    ).hexdigest()

    if hashed_password != check_hash:
        print('Неверный пароль')
        return None

    return user_id

def show_portfolio(logged_in, logged_id, base_currency=config.BASE_CURRENCY):
    if not logged_in:
        print('Сначала выполните login')
        return None

    if base_currency is None:
        base_currency = config.BASE_CURRENCY

    portfolios = from_json('data/portfolios.json') or []
    portfolio = next(
        (val for val in portfolios if val.get('user_id') == logged_id),
        None
    )

    if portfolio is None:
        print('Портфель не найден')
        return None

    wallets = portfolio.get('wallets', {})

    if not wallets:
        print('Кошельков нет')
        return None

    if base_currency != config.BASE_CURRENCY:
        print(f'Неизвестная базовая валюта {base_currency}')
        return None

    exchange_rates, _ = get_rates(base_currency)

    result = 0.0
    for currency_code, wallet in wallets.items():
        balance = wallet.get('balance', 0)

        if currency_code != config.BASE_CURRENCY:
            diff = balance * exchange_rates.get(currency_code, 0)
        else:
            diff = balance

        result += diff
        print(f'- {currency_code}: {balance} → {diff} {base_currency}')

    print(f'ИТОГО: {result} {base_currency}')

@log_action()
def buy(logged_id, currency, amount):

    if not logged_id:
        print('Сначала выполните login')
        return None

    amount = float(amount)

    if amount < 0:
        print(f'{amount} должен быть положительным числом')
        return None

    exchange_rates, _ = get_rates(config.BASE_CURRENCY)

    if currency not in exchange_rates.keys():
        print(f'Не удалось получить курс для {currency}→{config.BASE_CURRENCY}')
        return None

    portfolios = from_json('data/portfolios.json')
    portfolio_index = [i for i in range(len(portfolios)) if portfolios[i].get('user_id') == logged_id][0]
    portfolio = portfolios[portfolio_index]
    wallets = portfolio.get('wallets')

    if currency not in wallets.keys():
        wallets.update({currency: {"balance": 0.0}})

    before = wallets[currency]["balance"]
    wallets[currency]["balance"] += amount

    print(f'- {currency}: \n Было: {before} \n Стало: {wallets[currency]["balance"]}')

    portfolio['wallets'].update(wallets)
    portfolios[portfolio_index] = portfolio
    to_json('data/portfolios.json', portfolios)

    return True

@log_action()
def sell(logged_id, currency, amount):

    if not logged_id:
        print('Сначала выполните login')
        return None

    amount = float(amount)

    portfolios = from_json('data/portfolios.json')
    portfolio_index = [i for i in range(len(portfolios)) if portfolios[i].get('user_id') == logged_id][0]
    portfolio = portfolios[portfolio_index]

    wallets = portfolio.get('wallets')

    if currency not in wallets.keys():
        print(f'У вас нет кошелька {currency}. Добавьте валюту: она создаётся автоматически при первой покупке.')
        return None

    before = wallets[currency]["balance"]
    amount = float(amount)

    if before < amount:
        raise InsufficientFundsError(currency, before, amount)
    exchange_rates, _ = get_rates(config.BASE_CURRENCY)
    cost = amount * exchange_rates.get(currency)

    if wallets.get(config.BASE_CURRENCY) is None:
        wallets.update({config.BASE_CURRENCY: {"balance": 0.0}})
    wallets[config.BASE_CURRENCY]["balance"] += cost
    wallets[currency]["balance"] -= amount
    print(
        f'Продажа выполнена: {amount} {currency} по курсу {exchange_rates.get(currency)} {config.BASE_CURRENCY}/{currency}')
    print('Изменения в портфеле:')
    print(f'- {currency}: \n Было: {before} \n Стало: {wallets[currency]["balance"]}')

    portfolio['wallets'].update(wallets)
    portfolios[portfolio_index] = portfolio
    to_json('data/portfolios.json', portfolios)
    return True


def get_rate(curr_from, curr_to):
    cm = CurrencyMaker()

    try:
        cm.get_currency(curr_from)
        cm.get_currency(curr_to)
    except CurrencyNotFoundError:
        return None

    exchange_rates, update_dates = get_rates(curr_to)
    if not exchange_rates:
        return None

    rate = exchange_rates.get(curr_from)
    if rate is None:
        return None

    updated_at = update_dates[0] if update_dates else None

    return {
        "from": curr_from,
        "to": curr_to,
        "rate": rate,
        "reverse_rate": 1 / rate,
        "updated_at": updated_at,
    }

def update_rates(source):
    sources = [source] if source else None
    try:
        updater = RatesUpdater(config)
        count = updater.run_update(sources)
        if count > 0:
            print(f"Update successful. Total rates updated: {count}.")
        else:
            print("Update completed with errors. Check logs/parser.log for details.")
        return count
    except Exception as e:
        print(f"Update failed. Error: {e}. Check logs/parser.log for details.")
        return None

def show_rates(currency, top, base):
    base = config.BASE_CURRENCY if base is None else base
    rates_data = from_json("data/rates.json") or {}

    if (
        isinstance(rates_data, list)
        or not rates_data
        or "pairs" not in rates_data
        or not rates_data["pairs"]
    ):
        raise FileNotFoundError("Кеш пуст")

    pairs = rates_data["pairs"]
    last_update = rates_data.get("last_refresh", "unknown")
    print(f"Rates from cache (updated at {last_update}):")

    table = PrettyTable(["Pair", "Rate"])

    base_usd_pair = f"{base}_USD"
    base_usd_rate = pairs.get(base_usd_pair, {}).get("rate", 1.0) if base != "USD" else 1.0

    # 1) Показ конкретной валюты -> печатаем и выходим
    if currency:
        code = currency.strip().upper()
        cur_pair = f"{code}_{base}"
        cur_usd_pair = f"{code}_USD"
        cur_usd_rate = pairs.get(cur_usd_pair, {}).get("rate", 0)

        if cur_usd_rate == 0:
            print(f"Курс для '{currency}' не найден в кеше.")
            return None

        cur_base_rate = (cur_usd_rate / base_usd_rate) if base != "USD" else cur_usd_rate
        table.add_row([cur_pair, f"{cur_base_rate:.5f}"])
        print(table)
        return None

    # 2) Top N -> печатаем и выходим
    if top:
        top_n = int(top)
        crypto_usd = {
            k: v for k, v in pairs.items()
            if k.split("_")[0] in config.CRYPTO_CURRENCIES
        }
        sorted_crypto = sorted(
            crypto_usd.items(),
            key=lambda x: x[1]["rate"] / base_usd_rate,
            reverse=True,
        )[:top_n]

        for pair_usd, p in sorted_crypto:
            code = pair_usd.split("_")[0]
            rate_base = (p["rate"] / base_usd_rate) if base != "USD" else p["rate"]
            table.add_row([f"{code}_{base}", f"{rate_base:.2f}"])

        print(table)
        return None

    # 3) Иначе выводим всё
    for pair_usd, p in sorted(pairs.items()):
        code = pair_usd.split("_")[0]
        rate_usd = p["rate"]
        rate_base = (rate_usd / base_usd_rate) if base != "USD" else rate_usd
        pair_base = f"{code}_{base}"
        table.add_row([pair_base, f"{rate_base:.5f}"])

    print(table)
    return None

