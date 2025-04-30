import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
import pandas as pd
import json
from io import StringIO
import os

from src.utils import (
    get_time_for_greeting,
    get_data_time,
    get_path_and_period,
    get_card_with_spend,
    git_top_transaction,
    get_currency,
    get_stock,
    simple_search,
    find_mobile_payments,
    find_person_transfers
)


class TestUtilsFunctions(unittest.TestCase):
    """Тесты для функций модуля utils"""


    @patch('src.utils.datetime')
    def test_get_time_for_greeting(self, mock_datetime):
        """Тест проверяет корректность возвращаемого приветствия в зависимости от времени суток."""

        mock_datetime.now.return_value.hour = 8
        self.assertEqual(get_time_for_greeting(), "Доброе утро")

        mock_datetime.now.return_value.hour = 14
        self.assertEqual(get_time_for_greeting(), "Добрый день")

        mock_datetime.now.return_value.hour = 19
        self.assertEqual(get_time_for_greeting(), "Добрый вечер")

        mock_datetime.now.return_value.hour = 23
        self.assertEqual(get_time_for_greeting(), "Доброй ночи")


    def test_get_data_time(self):
        """Тест проверяет корректность преобразования формата даты и времени,
        а также правильность вычисления начала месяца."""

        test_date = "2023-05-15 14:30:00"
        expected = ["01.05.2023 14:30:00", "15.05.2023 14:30:00"]
        self.assertEqual(get_data_time(test_date), expected)

        custom_format = "%Y/%m/%d %H-%M-%S"
        test_date_custom = "2023/05/15 14-30-00"
        expected_custom = ["01.05.2023 14:30:00", "15.05.2023 14:30:00"]
        self.assertEqual(get_data_time(test_date_custom, custom_format), expected_custom)


    @patch('src.utils.pd.read_excel')
    def test_get_path_and_period(self, mock_read_excel):
        """Тест проверяет корректность фильтрации данных по периоду дати правильность сортировки результатов."""

        test_data = {
            "Дата операции": ["15.05.2023", "10.05.2023", "20.05.2023", "01.05.2023"],
            "Сумма операции": [100, 200, 300, 400],
            "Другие колонки": ["a", "b", "c", "d"]
        }
        test_df = pd.DataFrame(test_data)
        test_df["Дата операции"] = pd.to_datetime(test_df["Дата операции"], dayfirst=True)
        mock_read_excel.return_value = test_df

        period = ["01.05.2023 00:00:00", "15.05.2023 00:00:00"]
        result = get_path_and_period("dummy_path.xlsx", period)

        self.assertEqual(len(result), 3)
        self.assertEqual(result.iloc[0]["Дата операции"].strftime("%d.%m.%Y"), "01.05.2023")


    def test_get_card_with_spend(self):
        """Тест проверяет корректность: |Фильтрации только расходных операций| Форматирования номеров карт
        | Расчет кэшбэка"""

        test_data = {
            "Номер карты": ["1234****5678", "8765****4321", "1234****5678"],
            "Сумма операции": [-100, 200, -300],
            "Кэшбэк": [5, 0, 15],
            "Сумма операции с округлением": [-100, 200, -300]
        }
        test_df = pd.DataFrame(test_data)

        result = get_card_with_spend(test_df)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["last_digits"], "12345678")
        self.assertEqual(result[0]["cashback"], -1)


    def test_git_top_transaction(self):
        """Тест проверяет: |Корректность выбора топ-N транзакций| Правильность сортировки по сумме (по убыванию)
        | Формат возвращаемых данных"""

        test_data = {
            "Дата платежа": ["2023-05-01", "2023-05-02", "2023-05-03"],
            "Сумма операции": [100, 500, 300],
            "Категория": ["A", "B", "C"],
            "Описание": ["Desc1", "Desc2", "Desc3"]
        }
        test_df = pd.DataFrame(test_data)

        result = git_top_transaction(test_df, 2)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["amount"], "500")


    @patch('src.utils.requests.request')
    @patch.dict('os.environ', {'API_KEY_CURRENCY': 'test_key'})
    def test_get_currency(self, mock_request):
        """Тест проверяет: | Корректность работы с API (запрос и обработка ответа)| Парсинг JSON файла с валютами
        | Формат возвращаемых данных"""

        mock_response = MagicMock()
        mock_response.status_code = 200

        def side_effect(*args, **kwargs):
            from_currency = kwargs.get('params', {}).get('from')
            if from_currency == 'USD':
                return MagicMock(status_code=200, json=lambda: {
                    'query': {'from': 'USD'},
                    'result': 75.5
                })
            elif from_currency == 'EUR':
                return MagicMock(status_code=200, json=lambda: {
                    'query': {'from': 'EUR'},
                    'result': 85.3
                })
            return MagicMock(status_code=404)

        mock_request.side_effect = side_effect

        test_json_data = {"user_currencies": ["USD", "EUR"]}
        with patch('builtins.open', unittest.mock.mock_open(read_data=json.dumps(test_json_data))):
            result = get_currency("dummy_path.json")

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["currency"], "USD")
        self.assertEqual(result[0]["rates"], "75.5")
        self.assertEqual(result[1]["currency"], "EUR")
        self.assertEqual(result[1]["rates"], "85.3")


    @patch('src.utils.TDClient')
    def test_get_stock(self, mock_tdclient):
        """Тест проверяет: | Корректность работы с Twelve Data API| Парсинг JSON файла с акциями
        | Формат возвращаемых данных"""

        mock_instance = MagicMock()
        mock_time_series = MagicMock()
        mock_time_series.as_json.return_value = [{
            "close": "150.25",
            "datetime": "2023-05-15"
        }]
        mock_instance.time_series.return_value = mock_time_series
        mock_tdclient.return_value = mock_instance

        test_json_data = {"user_stocks": ["AAPL"]}
        with patch('builtins.open', unittest.mock.mock_open(read_data=json.dumps(test_json_data))):
            result = get_stock("dummy_path.json")

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["symbol"], "AAPL")
        self.assertEqual(result[0]["price"], 150.25)


    @patch('src.utils.pd.read_excel')
    def test_simple_search(self, mock_read_excel):
        """Тест проверяет: | Поиск по описанию транзакции| Поиск по категории транзакции
        | Регистронезависимость поиска"""

        test_data = {
            "Описание": ["Покупка в магазине", "Оплата услуг", "Перевод"],
            "Категория": ["Покупки", "Услуги", "Переводы"],
            "Другие колонки": ["a", "b", "c"]
        }
        test_df = pd.DataFrame(test_data)
        mock_read_excel.return_value = test_df

        result_desc = simple_search("dummy_path.xlsx", "магазин")
        self.assertEqual(len(result_desc), 1)
        self.assertEqual(result_desc[0]["Описание"], "Покупка в магазине")

        result_cat = simple_search("dummy_path.xlsx", "услуг")
        self.assertEqual(len(result_cat), 1)
        self.assertEqual(result_cat[0]["Категория"], "Услуги")


    @patch('src.utils.pd.read_excel')
    def test_find_mobile_payments(self, mock_read_excel):
        """Тест проверяет корректность поиска транзакций с номерами телефонов в описании.
        Должны находиться номера в различных форматах (+7, 8, 7)."""

        test_data = {
            "Описание": [
                "Пополнение +79161234567",
                "Оплата 89161234568",
                "Перевод без номера"
            ],
            "Категория": ["Пополнение", "Оплата", "Перевод"],
            "Другие колонки": ["a", "b", "c"]
        }
        test_df = pd.DataFrame(test_data)
        mock_read_excel.return_value = test_df

        result = find_mobile_payments("dummy_path.xlsx")

        self.assertEqual(len(result), 2)
        self.assertTrue("+79161234567" in result[0]["Описание"] or "89161234568" in result[0]["Описание"])


    @patch('src.utils.pd.read_excel')
    def test_find_person_transfers(self, mock_read_excel):
        """Тест проверяет корректность поиска переводов физическим лицам:
        1. Категория должна быть "Переводы"
        2. В описании должен быть шаблон имени (Фамилия И.О.)"""

        test_data = {
            "Описание": [
                "Иванов И.И.",
                "Петров П.П. благодарность",
                "Организация ООО Ромашка"
            ],
            "Категория": ["Переводы", "Переводы", "Услуги"],
            "Другие колонки": ["a", "b", "c"]
        }
        test_df = pd.DataFrame(test_data)
        mock_read_excel.return_value = test_df

        result = find_person_transfers("dummy_path.xlsx")

        self.assertEqual(len(result), 2)
        self.assertTrue("Иванов" in result[0]["Описание"] or "Петров" in result[1]["Описание"])
