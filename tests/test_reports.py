import json
from unittest.mock import patch

import pandas as pd
import pytest

from src.reports import get_dataframe, spending_by_category


@patch("src.reports.logger.info")
def test_spending_by_category_decorator(mock_logger, test_spending_df):
    """Тест для декоратора spending_by_category"""

    @spending_by_category(date="31.12.2021 16:44:00", category="Супермаркеты")
    def mock_get_data(*args, **kwargs):
        return test_spending_df

    result = mock_get_data()

    json_data = json.loads(result)
    assert len(json_data) == 1
    assert json_data[0]["Категория"] == "Супермаркеты"

    mock_logger.assert_called_once_with('Сформирован JSON-ответ "Отчеты"')


@patch("pandas.read_excel")
@patch("src.reports.logger.error")
def test_get_dataframe_error(mock_error, mock_read_excel):
    """Тест для обработки ошибок в get_dataframe"""

    mock_read_excel.side_effect = Exception("File not found")

    with pytest.raises(Exception) as exc_info:
        get_dataframe("test.xlsx")

    assert "Ошибка при чтении файла: File not found" in str(exc_info.value)

    mock_error.assert_called_once()


@patch("src.reports.logger.info")
def test_spending_by_category_empty_df(mock_logger):
    """Тест для пустого DataFrame"""
    @spending_by_category(date="31.12.2021 16:44:00", category="Супермаркеты")
    def mock_get_empty_data(*args, **kwargs):
        return pd.DataFrame()

    result = mock_get_empty_data()

    assert result == json.dumps([], ensure_ascii=False, indent=2)

    mock_logger.assert_not_called()


def test_spending_by_category_no_params(test_df):
    """Тест для декоратора без параметров"""
    @spending_by_category()
    def mock_get_data(*args, **kwargs):
        return test_df

    result = mock_get_data()

    json_data = json.loads(result)
    assert len(json_data) >= 0
