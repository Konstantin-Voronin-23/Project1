import json
import logging
import os
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Callable

import pandas as pd

log_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs", "reports.log")
logger = logging.getLogger("reports")
file_handler = logging.FileHandler(log_file, encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s - %(filename)s - %(funcName)s - %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)


def spending_by_category(date: str = None, category: str = None) -> Callable:  # type: ignore
    """Декоратор для фильтрации транзакций по категории и дате."""

    def decorator(func: Callable[..., pd.DataFrame]) -> Callable[..., str]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> str:

            df = func(*args, **kwargs)
            if df.empty:
                return json.dumps([], ensure_ascii=False, indent=2)

            end_date = datetime.strptime(date, "%d.%m.%Y %H:%M:%S") if date else datetime.now()
            start_date = end_date - timedelta(days=90)

            df["Дата операции"] = pd.to_datetime(df["Дата операции"], format="%d.%m.%Y %H:%M:%S")

            filtered = df[
                (df["Категория"] == category) & (df["Дата операции"] >= start_date) & (df["Дата операции"] <= end_date)
            ]

            result = filtered.to_dict("records")

            logger.info('Сформирован JSON-ответ "Отчеты"')
            return json.dumps(result, ensure_ascii=False, indent=2, default=str)

        return wrapper

    return decorator


@spending_by_category(date="31.12.2021 16:44:00", category="Супермаркеты")
def get_dataframe(filename: str) -> pd.DataFrame:
    """Функция читающая excel файл и возвращающая DataFrame."""
    try:
        df = pd.read_excel(filename)
        logger.info("DataFrame получен")
        return df
    except Exception as error:
        logger.error("%s", str(error), exc_info=True)
        raise Exception(f"Ошибка при чтении файла: {str(error)}")
