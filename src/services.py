import json
import logging
import os

from config import PATH_TO_EXCEL
from src.utils import find_mobile_payments, find_person_transfers, simple_search

log_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs", "services.log")
logger = logging.getLogger("services")
file_handler = logging.FileHandler(log_file, encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s - %(filename)s - %(funcName)s - %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)


def main_services() -> str:
    """Функция которая принимает путь до EXCEL файла, и реализует три поисковика тразанкций на выбор,
    1. по описанию или категории | 2. По мобильному номеру в описании | 3. по переводам физ лицам"""

    logger.info("Запуск функции сервиса по выбраному поиску |По описанию|По номеру телефона|По переводу физ лицам| ")
    print("\nВыберите тип поиска:")
    print("1 - По описанию или категории")
    print("2 - По мобильным номерам")
    print("3 - По переводам физлицам")

    choice = input("Ваш выбор (1-3): ")

    if choice == "1":
        print("\nВведите текст для поиска в описании или категории:")
        print("(оставьте пустым для вывода всех транзакций)")
        search_query = input("Поисковый запрос: ").strip()

        result = simple_search(PATH_TO_EXCEL, search_query)
        logger.info("Успех! Выбран поиск по описанию | категории")
        return json.dumps({"result": result}, ensure_ascii=False, indent=4)

    elif choice == "2":
        print("\nПоиск транзакций с мобильными номерами...")
        result = find_mobile_payments(PATH_TO_EXCEL)
        logger.info("Успех! Выбран поиск по номеру телефона")
        return json.dumps({"result": result}, ensure_ascii=False, indent=4)

    elif choice == "3":
        print("\nПоиск переводов физлицам...")
        result = find_person_transfers(PATH_TO_EXCEL)
        logger.info("Успех! Выбран поиск по переводам физ лицам")
        return json.dumps({"result": result}, ensure_ascii=False, indent=4)

    else:
        logger.error("error: Неверный выбор")
        return json.dumps({"error": "Неверный выбор"}, ensure_ascii=False, indent=4)
