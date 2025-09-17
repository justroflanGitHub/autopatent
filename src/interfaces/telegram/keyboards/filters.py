from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def create_filter_keyboard() -> InlineKeyboardMarkup:
    """Создание клавиатуры для настройки фильтров"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🌍 Страны поиска", callback_data="filter_countries"),
                InlineKeyboardButton(text="📑 Коды МПК", callback_data="filter_ipc")
            ],
            [
                InlineKeyboardButton(text="📋 Коды СПК", callback_data="filter_cpc"),
                InlineKeyboardButton(text="📅 Период", callback_data="filter_dates")
            ],
            [
                InlineKeyboardButton(text="❌ Сбросить фильтры", callback_data="reset_filters")
            ],
            [
                InlineKeyboardButton(text="🔄 Вернуться к поиску", callback_data="return_to_search")
            ]
        ]
    ) 