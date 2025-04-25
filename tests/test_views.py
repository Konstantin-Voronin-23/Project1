import json
from unittest.mock import MagicMock, patch

import pytest

from src.views import main_info


def test_main_info_basic() -> None:
    """Тест на проверку корректности работы программы"""

    with patch('src.views.get_data_time') as mock_get_data_time, \
            patch('src.views.get_path_and_period') as mock_get_path_and_period, \
            patch('src.views.get_time_for_greeting') as mock_get_time_for_greeting, \
            patch('src.views.get_card_with_spend') as mock_get_card_with_spend, \
            patch('src.views.git_top_transaction') as mock_git_top_transaction, \
            patch('src.views.get_currency') as mock_get_currency, \
            patch('src.views.get_stock') as mock_get_stock:

        mock_get_data_time.return_value = ("2023-01-01", "2023-01-31")
        mock_get_path_and_period.return_value = MagicMock()  # Просто заглушка
        mock_get_time_for_greeting.return_value = "Добрый день"
        mock_get_card_with_spend.return_value = [{"card": "Card1", "spend": 100}]
        mock_git_top_transaction.return_value = [{"amount": 100, "description": "Test"}]
        mock_get_currency.return_value = {"USD": 75.0}
        mock_get_stock.return_value = {"AAPL": 150.0}

        from src.views import main_info
        result = main_info("2023-01-01 12:00:00")

        data = json.loads(result)
        assert data["greeting"] == "Добрый день"
        assert len(data["cards"]) == 1
        assert len(data["top_transactions"]) == 1
        assert "USD" in data["currency_rates"]
        assert "AAPL" in data["stock_prices"]


def test_main_info_empty_data() -> None:
    """Тест на проверку, что программа корректно отрабатывает если приняты пустые данные"""

    with patch('src.views.get_data_time') as mock_get_data_time, \
            patch('src.views.get_path_and_period') as mock_get_path_and_period, \
            patch('src.views.get_time_for_greeting') as mock_get_time_for_greeting, \
            patch('src.views.get_card_with_spend') as mock_get_card_with_spend, \
            patch('src.views.git_top_transaction') as mock_git_top_transaction, \
            patch('src.views.get_currency') as mock_get_currency, \
            patch('src.views.get_stock') as mock_get_stock:

        mock_get_data_time.return_value = ("2023-01-01", "2023-01-31")
        mock_get_path_and_period.return_value = MagicMock()
        mock_get_time_for_greeting.return_value = ""
        mock_get_card_with_spend.return_value = []
        mock_git_top_transaction.return_value = []
        mock_get_currency.return_value = {}
        mock_get_stock.return_value = {}

        from src.views import main_info
        result = main_info("2023-01-01 12:00:00")

        data = json.loads(result)
        assert data["greeting"] == ""
        assert data["cards"] == []
        assert data["top_transactions"] == []
        assert data["currency_rates"] == {}
        assert data["stock_prices"] == {}


def test_main_info_error() -> None:
    """Тест отработки ошибок"""

    with patch('src.views.get_data_time') as mock_get_data_time:
        mock_get_data_time.side_effect = ValueError("Invalid date format")
        with pytest.raises(ValueError, match="Invalid date format"):
            main_info("invalid date")
