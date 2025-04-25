import json
from src.utils import simple_search, find_mobile_payments, find_person_transfers
from config import PATH_TO_EXCEL
from typing import Optional


def main_services() -> str:
    """Функция которая принимает путь до EXCEL файла, и реализует три поисковика тразанкций на выбор,
    1. по описанию или категории | 2. По мобильному номеру в описании | 3. по переводам физ лицам"""

    # 1) Поиска транзакций по описанию или категории

    search_transactions = simple_search(PATH_TO_EXCEL, "")

    # 2) Поиск транзакций где в описании указан мобильный телефон

    search_transactions_mobile = find_mobile_payments(PATH_TO_EXCEL)

    # 3) Поиск транзакций по переводам физ лицам

    search_transactions_person = find_person_transfers(PATH_TO_EXCEL)

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
        return json.dumps({"result": result}, ensure_ascii=False, indent=4)

    elif choice == "2":
        print("\nПоиск транзакций с мобильными номерами...")
        result = find_mobile_payments(PATH_TO_EXCEL)
        return json.dumps({"result": result}, ensure_ascii=False, indent=4)

    elif choice == "3":
        print("\nПоиск переводов физлицам...")
        result = find_person_transfers(PATH_TO_EXCEL)
        return json.dumps({"result": result}, ensure_ascii=False, indent=4)

    else:
        return json.dumps({"error": "Неверный выбор"}, ensure_ascii=False, indent=4)
