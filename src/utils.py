import json
from datetime import datetime
import pandas as pd
from pandas import DataFrame
import requests
import os
from dotenv import load_dotenv
from twelvedata import TDClient
import logging


log_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs", "utils.log")
logger = logging.getLogger("utils")
file_handler = logging.FileHandler(log_file, encoding="utf-8")
file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)


load_dotenv()
API_KEY_CURRENCY = os.getenv('API_KEY_CURRENCY')
API_KEY_SP500 = os.getenv('API_KEY_SP500')
URL_CURRENCY="https://api.apilayer.com/exchangerates_data/convert"


def get_time_for_greeting():
    """Функция возвращает приветствие «Доброе утро» / «Добрый день» / «Добрый вечер» / «Доброй ночи»
    в зависимости от текущего времени"""

    logger.info(f"Запуск функции приветствия")
    user_datetime_hour = datetime.now().hour

    if 5 <= user_datetime_hour < 12:
        logger.info(f"Успех! Доброе утро, при актуальном времени с 5 утра до 12")
        return "Доброе утро"
    elif 12 <= user_datetime_hour < 18:
        logger.info(f"Успех! Добрый день, при актуальном времени с 12 дня до 18")
        return  "Добрый день"
    elif 18 <= user_datetime_hour < 22:
        logger.info(f"Успех! Добрый вечер, при актуальном времени 18 вечера до 22 вечера")
        return "Добрый вечер"
    else:
        logger.info(f"Успех! Доброй ночи, при актуальном времени с 22 часов вечера до 5 утра")
        return "Доброй ночи"


def get_data_time(date_time: str, date_format: str="%Y-%m-%d %H:%M:%S") -> list[str]:
    """Функция изменения формата даты и времени"""

    logger.info(f"Запуск функции изменения формата даты и времени")
    dt = datetime.strptime(date_time, date_format)
    start_of_month = dt.replace(day=1)

    logger.info(f"Успех! Данные даты и времени успешно изменены")
    return [
        start_of_month.strftime("%d.%m.%Y %H:%M:%S"),
        dt.strftime("%d.%m.%Y %H:%M:%S")
    ]


def get_path_and_period(path_to_file: str, period_date: list) -> DataFrame:
    """Функция принимает путь к Excel файлу и список дат, и возвращает табилицу в заданном периоде"""

    logger.info(f"Запуск функции среза по дате в excel файле")
    df = pd.read_excel(path_to_file, sheet_name="Отчет по операциям")

    df["Дата операции"] = pd.to_datetime(df["Дата операции"], dayfirst=True)
    start_date = datetime.strptime(period_date[0], "%d.%m.%Y %H:%M:%S")
    end_date = datetime.strptime(period_date[1], "%d.%m.%Y %H:%M:%S")
    filter_df = df[
        (df["Дата операции"] >= start_date) &
        (df["Дата операции"] <= end_date)
    ]
    sorted_df = filter_df.sort_values(by="Дата операции", ascending=True)

    logger.info(f"Успех! Получен срез даты от и до")
    return sorted_df

def get_card_with_spend(sorted_df: DataFrame) -> list[dict]:
    """Функция принимает DataFrame и возвращает список карт с расходами"""

    logger.info(f"Запуск функции со списком карт по которым были расходы")
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
            last_digits = str(row["Номер карты"]).replace("*", "")
            total_spent = row["Сумма операции с округлением"]
            cashback = total_spent // 100
            row = {
                "last_digits": last_digits,
                "total_spent": total_spent,
                "cashback": cashback
            }
            card_spend_transactions.append(row)

    logger.info(f"Успех! Данные получены без ошибок")
    return card_spend_transactions


def git_top_transaction(sorted_df: DataFrame, get_top):
    """Функция принимает DataFrame и возвращает топ-транзакций по сумме платежа"""

    logger.info(f"Запуск функции по топ-транзакциям")
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
    logger.info(f"Успех! Получен топ-5 по сумме платежа")
    return top_pay_transactions


def get_currency(path_to_json: str) -> list[dict]:
    """Функция принимает на вход path_to_json и возвращает курс валют"""

    logger.info(f"Запуск функции которая получает актуальный курс валют")
    currency_rates = []
    with open(path_to_json, "r", encoding="utf-8") as file:
        data = json.load(file)
        currencys = data["user_currencies"]
        for currency in currencys:
            params = {
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
        logger.info(f"Успех! Получен курс валют")
        return currency_rates


def get_stock(path_to_json: str) -> list[dict]:
    """Функция принимает на вход path_to_json и возвращает курс акций"""

    logger.info(f"Запуск функции которая получает актуальный курс акций SP500")
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
        logger.info(f"Успех! Получен курс акций SP500")
        return stock_rates
