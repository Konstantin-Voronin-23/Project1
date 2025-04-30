import json
import logging
import os

from config import PATH_TO_EXCEL, PATH_TO_USER_SETTINGS
from src.utils import (get_card_with_spend, get_currency, get_data_time, get_path_and_period, get_stock,
                       get_time_for_greeting, git_top_transaction)

log_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs", "views.log")
logger = logging.getLogger("views")
file_handler = logging.FileHandler(log_file, encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s - %(filename)s - %(funcName)s - %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)


logger.info("Запуск функции главной страницы с заданными параметрами")
def main_info(date_time: str) -> str:
    """Функция и главная функция, принимающая на вход строку с датой и временем в формате YYYY-MM-DD HH:MM:SS
    и возвращающую JSON-ответ"""

    # Срез всего экселя на диапозон
    time_period = get_data_time(date_time)
    sorted_df = get_path_and_period(PATH_TO_EXCEL, time_period)

    # 1) Приветствие

    logger.info("Запуск функции приветствия")
    greeting = get_time_for_greeting()

    # 2) По каждой карте

    logger.info(f"Запуск функции со списком карт по которым были расходы")
    cards = get_card_with_spend(sorted_df)

    # 3) Топ-5 транзакций по сумме платежа

    logger.info("Запуск функции по топ-транзакциям")
    top_transaction = git_top_transaction(sorted_df, 5)

    # 4) Курс валют

    logger.info("Запуск функции которая получает актуальный курс валют")
    currency_rates = get_currency(PATH_TO_USER_SETTINGS)

    # 5) Стоимость акций из S&P500

    logger.info("Запуск функции которая получает актуальный курс акций SP500")
    stock_prices = get_stock(PATH_TO_USER_SETTINGS)

    data = {
        "greeting": greeting,
        "cards": cards,
        "top_transactions": top_transaction,
        "currency_rates": currency_rates,
        "stock_prices": stock_prices
    }

    json_data = json.dumps(data, ensure_ascii=False, indent=4)

    logger.info("Успех! Получен отфильтрованный json файл по заданным параметрам")
    return json_data
