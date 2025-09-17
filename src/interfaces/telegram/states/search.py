# src/interfaces/telegram/states/search.py

from aiogram.fsm.state import State, StatesGroup


class SearchStates(StatesGroup):
    """Состояния для процесса поиска патентов"""
    choosing_method = State()  # Выбор метода поиска
    waiting_for_query = State()  # Ожидание поискового запроса
    
    # Состояния для фильтров
    setting_countries = State()  # Ввод стран
    setting_ipc_codes = State()  # Ввод кодов МПК
    setting_cpc_codes = State()  # Ввод кодов СПК
    setting_date_from = State()  # Ввод начальной даты
    setting_date_to = State()  # Ввод конечной даты
    confirming_filters = State()  # Подтверждение фильтров