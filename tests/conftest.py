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
