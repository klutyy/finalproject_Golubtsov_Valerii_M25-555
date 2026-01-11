# ValutaTrade Hub

Консольное приложение для управления валютным портфелем.  
Позволяет регистрироваться, авторизовываться, покупать и продавать валюту,  
просматривать портфель и получать актуальные курсы валют.

Проект работает через терминал и использует JSON-файлы в качестве хранилища данных.
---

## Установка

### Вариант 1 — через Poetry
```bash
poetry install
```

### Вариант 2 - через Makefile

```
make install
```

## Запуск приложения

### Вариант 1 — через Poetry
```bash
poetry run project
```

### Вариант 2 - через Makefile
```
make project
```

## Хранилище данных

Для простоты проект использует JSON-файлы:

`data/users.json` — пользователи

`data/portfolios.json` — портфели и кошельки пользователей

`data/rates.json` — кеш актуальных курсов валют

`data/exchange_rates.json` — история обновлений курсов

## Поддерживаемые валюты

Фиатные: `USD`, `EUR`, `GBP`, `RUB`

Криптовалюты: `BTC`, `ETH`, `SOL`

Курсы валют обновляются через внешние API и кешируются локально.
---

## Управление таблицами

### Команды CLI
**Для получения всех команд используйте help*

| Команда | Описание |
|--------|----------|
| `register --username <str> --password <str>` | Регистрация нового пользователя с указанными именем и паролем [conversation_history:1] |
| `login --username <str> --password <str>` | Авторизация пользователя с проверкой имени и пароля [conversation_history:1] |
| `show-portfolio` | Показать портфолио текущего пользователя в базовой валюте [conversation_history:1] |
| `show-portfolio --base <str>` | Показать портфолио текущего пользователя в указанной базовой валюте [conversation_history:1] |
| `buy --currency <str> --amount <float>` | Купить указанное количество валюты и добавить её в портфель [conversation_history:1] |
| `sell --currency <str> --amount <float>` | Продать указанное количество валюты из портфеля [conversation_history:1] |
| `get-rate --from <str> --to <str>` | Получить текущий курс между двумя валютами [conversation_history:1] |
| `update-rates` | Обновить актуальные курсы валют из внешнего источника [conversation_history:1] |
| `show-rates` | Показать список всех актуальных курсов валют [conversation_history:1] |
| `show-rates --top <int>` | Показать N самых дорогих валют по текущему курсу [conversation_history:1] |
| `show-rates --currency <str>` | Показать курс конкретной валюты относительно базовой [conversation_history:1] |


### Пример

# ASCIINEMA
[![asciicast](https://asciinema.org/a/FqKFHRo0SWnWXb7p.svg)](https://asciinema.org/a/FqKFHRo0SWnWXb7p)