import pandas as pd
import pytest


@pytest.fixture
def mock_excel_path():
    """Фикстура, возвращающая фейковый путь к Excel файлу для тестирования."""
    return "fake/path/to/excel.xlsx"


@pytest.fixture
def mock_simple_search_result():
    """Фикстура, возвращающая моковые данные для функции simple_search."""
    return [{"amount": 100, "description": "Различные товары"}]


@pytest.fixture
def mock_mobile_payments_result():
    """Фикстура, возвращающая моковые данные для функции find_mobile_payments."""
    return [{"amount": 50, "description": "Пополнение телефона 79123456789"}]


@pytest.fixture
def mock_person_transfers_result():
    """Фикстура, возвращающая моковые данные для функции find_person_transfers."""
    return [{"amount": 200, "description": "Перевод Иванову И.И."}]


@pytest.fixture
def test_df():
    """Фикстура с тестовыми данными DataFrame"""
    return pd.DataFrame(
        {
            "Дата операции": ["01.01.2023 12:00:00", "15.01.2023 12:00:00"],
            "Номер карты": ["1234****5678", "8765****4321"],
            "Сумма операции": [-100, 200],
            "Кэшбэк": [1, 0],
            "Сумма операции с округлением": [-100, 200],
            "Категория": ["Магазин", "Ресторан"],
            "Описание": ["Покупка +79123456789", "Обед"],
            "Дата платежа": ["02.01.2023", "16.01.2023"],
            "Статус": ["OK", "OK"],
            "Валюта операции": ["RUB", "RUB"],
            "Валюта платежа": ["RUB", "RUB"],
            "Сумма платежа": [-100, 200],  # Добавляем недостающую колонку
        }
    )


@pytest.fixture
def test_spending_df():
    data = {
        "Дата операции": ["31.12.2021 16:44:00", "15.01.2022 12:00:00"],
        "Категория": ["Супермаркеты", "Рестораны"],
        "Сумма операции": [1000, 2000],
        "Описание": ["Покупки в магазине", "Обед в кафе"],
    }
    return pd.DataFrame(data)
