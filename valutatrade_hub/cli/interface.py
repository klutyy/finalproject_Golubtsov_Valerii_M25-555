import shlex

import prompt

from valutatrade_hub.core.usecases import (
    buy,
    get_rate,
    login,
    register,
    sell,
    show_portfolio,
    show_rates,
    update_rates,
)


def print_help():
    print('Регистрация пользователя: register --username <str> --password <str>')
    print('Авторизация пользователя: login --username <str> --password <str>')
    print('Показать портфолио пользователя в базовой валюте: show-portfolio')
    print('Показать портфолио пользователя в кастомной валюте: show-portfolio --base <str>')
    print('Купить валюту: buy --currency <str> --amount <float>')
    print('Продать валюту: sell --currency <str> --amount <float>')
    print('Получить текущий курс: get-rate --from <str> --to <str>')
    print('Получить актуальные курсы валют: update-rates')
    print('Показать список актуальных курсов: show-rates')
    print('Показать N самых дорогих валют: show-rates --top <int>')
    print('Показать курс конкретной валюты: show-rates --currency <str>')


logged_in = False
logged_id = None


def _get_arg(args, flag):
    if flag in args:
        idx = args.index(flag)
        if idx + 1 < len(args):
            return args[idx + 1]
    return None


def run():
    global logged_in
    global logged_id

    print_help()

    while True:
        query = prompt.string('Введите команду: ').strip()
        if not query:
            continue

        args = shlex.split(query)
        command = args[0]

        match command:
            case 'register':
                username = _get_arg(args, '--username')
                password = _get_arg(args, '--password')

                if not username or not password:
                    print('Неверные аргументы. Пример: register --username alice --password 1234')
                    continue

                user_id = register(username, password)
                if user_id is not None:
                    masked = '*' * len(password)
                    print(
                        f"Пользователь {username} зарегистрирован (id={user_id}). "
                        f"Войдите: login --username {username} --password {masked}"
                    )

            case 'login':
                username = _get_arg(args, '--username')
                password = _get_arg(args, '--password')

                if not username or not password:
                    print('Неверные аргументы. Пример: login --username alice --password 1234')
                    continue

                logged_id = login(username, password)
                logged_in = logged_id is not None

                if logged_in:
                    print(f'Вы вошли как {username}')

            case 'show-portfolio':
                base_currency = _get_arg(args, '--base')
                show_portfolio(logged_in, logged_id, base_currency=base_currency)

            case 'buy':
                currency = _get_arg(args, '--currency')
                amount = _get_arg(args, '--amount')

                if not currency or amount is None:
                    print('Неверные аргументы. Пример: buy --currency BTC --amount 0.01')
                    continue

                ok = buy(logged_id, currency, amount)
                if ok is None:
                    print('Покупка не выполнена')

            case 'sell':
                currency = _get_arg(args, '--currency')
                amount = _get_arg(args, '--amount')

                if not currency or amount is None:
                    print('Неверные аргументы. Пример: sell --currency BTC --amount 0.01')
                    continue

                ok = sell(logged_id, currency, amount)
                if ok is None:
                    print('Продажа не выполнена')

            case 'get-rate':
                curr_from = _get_arg(args, '--from')
                curr_to = _get_arg(args, '--to')

                if not curr_from or not curr_to:
                    print('Неверные аргументы. Пример: get-rate --from EUR --to USD')
                    continue

                result = get_rate(curr_from, curr_to)
                if result is None:
                    print(f'Курс {curr_from}→{curr_to} недоступен. Повторите попытку позже.')
                else:
                    updated = result.get('updated_at')
                    print(f"Курс {curr_from}→{curr_to}: {result['rate']} (обновлено: {updated})")
                    print(f"Обратный курс {curr_to}→{curr_from}: {result['reverse_rate']}")

            case 'update-rates':
                # В help у тебя "update-rates" без аргументов, но если есть флаг --source, прочитаем.
                source = _get_arg(args, '--source')
                update_rates(source)

            case 'show-rates':
                currency = _get_arg(args, '--currency')
                top = _get_arg(args, '--top')
                base = _get_arg(args, '--base')

                show_rates(currency, top, base)

            case 'help':
                print_help()

            case 'exit':
                break

            case _:
                print(f'Функции {command} нет. Попробуйте снова.')
