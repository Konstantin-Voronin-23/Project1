from src.services import main_services
from src.views import main_info
from src.reports import get_dataframe
from config import PATH_TO_EXCEL


if __name__ == "__main__":
    print(main_info("2018-04-22 18:16:00"))
    print(main_services())
    print(get_dataframe(PATH_TO_EXCEL))
