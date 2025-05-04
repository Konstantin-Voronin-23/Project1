import json
from unittest.mock import patch

import pytest

from src.services import main_services


@pytest.mark.parametrize("choice, input_value, expected_key", [
    ("1", "тест", "result"),  # Поиск по описанию
    ("2", "", "result"),  # Поиск мобильных платежей
    ("3", "", "result"),  # Поиск переводов
    ("4", "", "error"),  # Неверный выбор
])
def test_main_services_choices(choice, input_value, expected_key, mock_excel_path,
                               mock_simple_search_result, mock_mobile_payments_result,
                               mock_person_transfers_result):
    """Параметризованный тест для проверки различных вариантов выбора пользователя."""

    with patch('config.PATH_TO_EXCEL', mock_excel_path), \
            patch('src.utils.simple_search', return_value=mock_simple_search_result), \
            patch('src.utils.find_mobile_payments', return_value=mock_mobile_payments_result), \
            patch('src.utils.find_person_transfers', return_value=mock_person_transfers_result), \
            patch('builtins.input', side_effect=[choice, input_value]):
        result = main_services()
        result_data = json.loads(result)

        assert expected_key in result_data


def simple_search_integration():
    """Тест поиска по описанию"""

    with patch('src.services.simple_search', return_value=[{"test": "data"}]):
        with patch('builtins.input', return_value="1"):
            result = main_services()
            assert '"result"' in result


def test_main_services_with_patched_input(mock_excel_path, mock_mobile_payments_result):
    """Тест с подменой пользовательского ввода."""

    with patch('config.PATH_TO_EXCEL', mock_excel_path), \
            patch('src.utils.find_mobile_payments', return_value=mock_mobile_payments_result), \
            patch('builtins.input', return_value="2"):
        result = main_services()
        result_data = json.loads(result)

        assert "result" in result_data
        # Проверяем только структуру ответа, так как данные могут отличаться
        assert isinstance(result_data["result"], list)


def test_invalid_choice(mock_excel_path):
    """Тест обработки неверного выбора пользователя."""

    with patch('config.PATH_TO_EXCEL', mock_excel_path), \
            patch('builtins.input', return_value="5"):
        result = main_services()
        result_data = json.loads(result)

        assert "error" in result_data
        assert result_data["error"] == "Неверный выбор"
