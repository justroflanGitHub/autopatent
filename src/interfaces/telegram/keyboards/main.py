# src/interfaces/telegram/keyboards/main.py

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def create_main_keyboard() -> ReplyKeyboardMarkup:
    """Создание основной клавиатуры"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="🔍 Семантический поиск"),
                KeyboardButton(text="🎯 Точный поиск")
            ],
            [
                KeyboardButton(text="❓ Помощь")
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )


def create_exact_search_keyboard() -> ReplyKeyboardMarkup:
    """Создание клавиатуры для режима точного поиска"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="⚙️ Настроить фильтры"),
                KeyboardButton(text="👁 Текущие фильтры")
            ],
            [
                KeyboardButton(text="🔄 Вернуться в главное меню")
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )