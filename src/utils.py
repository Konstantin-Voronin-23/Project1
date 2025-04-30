import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List

import pandas as pd
import requests
from dotenv import load_dotenv
from pandas import DataFrame
from twelvedata import TDClient  # type: ignore

log_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs", "utils.log")
logger = logging.getLogger("utils")
file_handler = logging.FileHandler(log_file, encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s - %(filename)s - %(funcName)s - %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)


load_dotenv()
API_KEY_CURRENCY = os.getenv('API_KEY_CURRENCY')
API_KEY_SP500 = os.getenv('API_KEY_SP500')
URL_CURRENCY = "https://api.apilayer.com/exchangerates_data/convert"


def get_time_for_greeting() -> str:
    """Функция возвращает приветствие «Доброе утро» / «Добрый день» / «Добрый вечер» / «Доброй ночи»
    в зависимости от текущего времени"""

    logger.info("Запуск функции приветствия")
    user_datetime_hour = datetime.now().hour

    if 5 <= user_datetime_hour < 12:
        logger.info("Успех! Доброе утро")
        return "Доброе утро"
    elif 12 <= user_datetime_hour < 18:
        logger.info("Успех! Добрый день")
        return "Добрый день"
    elif 18 <= user_datetime_hour < 22:
        logger.info("Успех! Добрый вечер")
        return "Добрый вечер"
    else:
        logger.info("Успех! Доброй ночи")
        return "Доброй ночи"


def get_data_time(date_time: str, date_format: str = "%Y-%m-%d %H:%M:%S") -> list[str]:
    """Функция изменения формата даты и времени"""

    logger.info(f"Запуск функции изменения формата даты и времени с аргументами {date_time} и {date_format}")
    dt = datetime.strptime(date_time, date_format)
    start_of_month = dt.replace(day=1)

    logger.info("Успех! Данные даты и времени успешно изменены")
    return [
        start_of_month.strftime("%d.%m.%Y %H:%M:%S"),
        dt.strftime("%d.%m.%Y %H:%M:%S")
    ]


def get_path_and_period(path_to_file: str, period_date: list) -> DataFrame:
    """Функция принимает путь к Excel файлу и список дат, и возвращает табилицу в заданном периоде"""

    logger.info(f"Запуск функции среза по дате в excel файле с аргументами {path_to_file} и {period_date}")
    df = pd.read_excel(path_to_file, sheet_name="Отчет по операциям")

    df["Дата операции"] = pd.to_datetime(df["Дата операции"], dayfirst=True)
    start_date = datetime.strptime(period_date[0], "%d.%m.%Y %H:%M:%S")
    end_date = datetime.strptime(period_date[1], "%d.%m.%Y %H:%M:%S")
    filter_df = df[
        (df["Дата операции"] >= start_date) & (df["Дата операции"] <= end_date)
    ]
    sorted_df = filter_df.sort_values(by="Дата операции", ascending=True)

    logger.info("Успех! Получен срез даты")
    return sorted_df


def get_card_with_spend(sorted_df: DataFrame) -> List[Dict[str, Any]]:
    """Функция принимает DataFrame и возвращает список карт с расходами"""

    logger.info(f"Запуск функции со списком карт по которым были расходы с аргументом {sorted_df}")
    card_spend_transactions = []
    card_sorted = sorted_df[
        [
            "Номер карты",
            "Сумма операции",
            "Кэшбэк",
            "Сумма операции с округлением"
        ]
    ]
    for index, row in card_sorted.iterrows():
        if row['Сумма операции'] < 0:
            card_spend_transactions.append({
                "last_digits": str(row["Номер карты"]).replace("*", ""),
                "total_spent": row["Сумма операции с округлением"],
                "cashback": row["Сумма операции с округлением"] // 100
            })

    logger.info("Успех! Данные получены без ошибок")
    return card_spend_transactions


def git_top_transaction(sorted_df: DataFrame, get_top: int) -> list[dict]:
    """Функция принимает DataFrame и возвращает топ-транзакций по сумме платежа"""

    logger.info(f"Запуск функции по топ-транзакциям с аргументами {sorted_df} и {get_top}")
    top_pay_transactions = []
    sorted_pay_df = sorted_df.sort_values(by="Сумма операции", ascending=False)
    top_transactions = sorted_pay_df.head(get_top)
    top_transactions_sorted = top_transactions[
        [
            "Дата платежа",
            "Сумма операции",
            "Категория",
            "Описание"
        ]
    ]
    for index, row in top_transactions_sorted.iterrows():
        transaction = {
            "date": f"{row['Дата платежа']}",
            "amount": f"{row['Сумма операции']}",
            "category": f"{row['Категория']}",
            "description": f"{row['Описание']}"
        }
        top_pay_transactions.append(transaction)
    logger.info("Успех! Получен топ-5 по сумме платежа")
    return top_pay_transactions


def get_currency(path_to_json: str) -> list[dict]:
    """Функция принимает на вход path_to_json и возвращает курс валют"""

    logger.info(f"Запуск функции которая получает актуальный курс валют с аргументом {path_to_json}")
    currency_rates = []
    with open(path_to_json, "r", encoding="utf-8") as file:
        data = json.load(file)
        currencys = data["user_currencies"]
        for currency in currencys:
            params: dict[str, str | int | float] = {
                "amount": 1,
                "from": f"{currency}",
                "to": "RUB"
            }
            headers = {
                "apikey": f"{API_KEY_CURRENCY}"
            }
            response = requests.request("GET", URL_CURRENCY, headers=headers, params=params)

            status_code = response.status_code
            if status_code == 200:
                result = response.json()
                currency_code_response = result['query']['from']
                currency_amount = round(result['result'], 2)
                currency_rates.append({
                    "currency": f"{currency_code_response}",
                    "rates": f"{currency_amount}"
                })
        logger.info("Успех! Получен курс валют")
        return currency_rates


def get_stock(path_to_json: str) -> list[dict]:
    """Функция принимает на вход path_to_json и возвращает курс акций"""

    logger.info(f"Запуск функции которая получает актуальный курс акций SP500 с аргументом {path_to_json}")
    stock_rates = []
    td = TDClient(apikey=API_KEY_SP500)
    with open(path_to_json, "r", encoding="utf-8") as file:
        data = json.load(file)
        stocks = data["user_stocks"]

        for stock in stocks:
            ts = td.time_series(
                symbol=stock,
                interval="1min",
                outputsize=1
            )
            data = ts.as_json()[0]

            stock_rates.append({
                "symbol": stock,
                "price": float(data["close"]),
                "datetime": data["datetime"]
            })
        logger.info("Успех! Получен курс акций SP500")
        return stock_rates


def simple_search(path_to_file: str, search_query: str) -> List[Dict[str, Any]]:
    """Простой поиск по описанию или категории"""

    logger.info(f"Запуск функции простого поиска с аргументами {path_to_file} и {search_query}")
    df = pd.read_excel(path_to_file, sheet_name="Отчет по операциям", engine='openpyxl')
    mask = (df['Описание'].str.contains(search_query, case=False, na=False)) | \
           (df['Категория'].str.contains(search_query, case=False, na=False))

    json_str = df[mask].to_json(orient='records', force_ascii=False)
    result: List[Dict[str, Any]] = json.loads(json_str)
    logger.info("Успех! Данные отфильтрованы по описанию | категории")
    return result


def find_mobile_payments(path_to_file: str) -> List[Dict[str, Any]]:
    """Поиск транзакций с мобильными номерами в описании"""

    logger.info(f"Запуск функции поиска транзакций с мобильными номерами в описании с аргмуентом {path_to_file}")
    df = pd.read_excel(path_to_file, sheet_name="Отчет по операциям", engine='openpyxl')
    phone_pattern = r'(?:\+7|7|8)?[\s\-]?(?:[489][0-9]{2})?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}'

    mask = df['Описание'].str.contains(phone_pattern, na=False)

    json_str = df[mask].to_json(orient='records', force_ascii=False)
    result: List[Dict[str, Any]] = json.loads(json_str)
    logger.info("Успех! Данные с номером телефона в описании транзакций отфильтрованы")
    return result


def find_person_transfers(path_to_file: str) -> List[Dict[str, Any]]:
    """Поиск переводов физическим лицам"""

    logger.info(f"Запуск функции поиска переводов физическим лицам с аргументом {path_to_file}")
    df = pd.read_excel(path_to_file, sheet_name="Отчет по операциям", engine='openpyxl')
    category_condition = (df['Категория'] == 'Переводы')
    name_pattern = r'^[А-ЯЁ][а-яё]+\s[А-ЯЁ]\.'
    description_condition = df['Описание'].str.contains(name_pattern, na=False)
    mask = category_condition & description_condition

    json_str = df[mask].to_json(orient='records', force_ascii=False)
    result: List[Dict[str, Any]] = json.loads(json_str)
    logger.info("Успех! Данные с переводами физ лицам отфильтрованы")
    return result
