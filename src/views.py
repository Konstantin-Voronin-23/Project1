from typing import Dict, Any
import json
from config import PATH_TO_EXCEL, PATH_TO_USER_SETTINGS
from src.utils import (get_time_for_greeting,
                       get_data_time,
                       get_path_and_period,
                       get_card_with_spend,
                       get_card_with_spend,
                       git_top_transaction,
                       get_currency,
                       get_stock
                       )


def main_info(date_time: str) -> Dict[str, Any]:
    """Функция и главная функция, принимающая на вход строку с датой и временем в формате YYYY-MM-DD HH:MM:SS
    и возвращающую JSON-ответ"""

    # Срез всего экселя на диапозон
    time_period = get_data_time(date_time)
    sorted_df = get_path_and_period(PATH_TO_EXCEL, time_period)

    # 1) Приветствие

    greeting = get_time_for_greeting()

    # 2) По каждой карте

    cards = get_card_with_spend(sorted_df)

    # 3) Топ-5 транзакций по сумме платежа

    top_transaction = git_top_transaction(sorted_df, 5)

    # 4) Курс валют

    currency_rates = get_currency(PATH_TO_USER_SETTINGS)

    # 5) Стоимость акций из S&P500

    stock_prices = get_stock(PATH_TO_USER_SETTINGS)

    data = {
        "greeting": greeting,
        "cards": cards,
        "top_transactions": top_transaction,
        "currency_rates": currency_rates,
        "stock_prices": stock_prices
    }

    json_data = json.dumps(data, ensure_ascii=False, indent=4)

    return json_data
