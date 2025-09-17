import logging
from datetime import datetime, timedelta
from typing import Dict, Optional

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from src.domain.entities.search_filter import SearchFilter
from src.interfaces.telegram.keyboards.filters import create_filter_keyboard
from src.interfaces.telegram.keyboards.main import create_exact_search_keyboard
from src.interfaces.telegram.states.search import SearchStates

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data == "filter_countries")
async def process_countries_setting(callback: CallbackQuery, state: FSMContext):
    """Обработка установки стран поиска"""
    await callback.message.edit_text(
        "🌍 Введите коды стран через запятую (например: RU, US, EP)\n\n"
        "Доступные коды:\n"
        "🇷🇺 RU - Россия\n"
        "🇺🇸 US - США\n"
        "🇪🇺 EP - Европейский патент\n"
        "🇰🇿 KZ - Казахстан\n"
        "🇧🇾 BY - Беларусь"
    )
    await state.set_state(SearchStates.setting_countries)


@router.callback_query(F.data == "filter_ipc")
async def process_ipc_setting(callback: CallbackQuery, state: FSMContext):
    """Обработка установки кодов МПК"""
    await callback.message.edit_text(
        "📑 Введите коды МПК через запятую\n"
        "Пример: A61K6/00, C07D403/12"
    )
    await state.set_state(SearchStates.setting_ipc_codes)


@router.callback_query(F.data == "filter_cpc")
async def process_cpc_setting(callback: CallbackQuery, state: FSMContext):
    """Обработка установки кодов СПК"""
    await callback.message.edit_text(
        "📋 Введите коды СПК через запятую\n"
        "Пример: Y02E10/50, H01L31/00"
    )
    await state.set_state(SearchStates.setting_cpc_codes)


@router.callback_query(F.data == "filter_dates")
async def process_dates_setting(callback: CallbackQuery, state: FSMContext):
    """Обработка установки периода поиска"""
    await callback.message.edit_text(
        "📅 Введите глубину поиска в годах (от 1 до 30)\n"
        "Например: 20 (будут найдены патенты за последние 20 лет)"
    )
    await state.set_state(SearchStates.setting_date_from)


@router.callback_query(F.data == "return_to_search")
async def return_to_search(callback: CallbackQuery, state: FSMContext):
    """Возврат к поиску"""
    await callback.message.delete()  # Удаляем сообщение с фильтрами
    await callback.message.answer(
        "✅ Можете продолжить поиск с текущими фильтрами",
        reply_markup=create_exact_search_keyboard()
    )
    await state.set_state(SearchStates.waiting_for_query)


@router.message(F.text == "🔄 Вернуться к поиску")
async def handle_return_to_search(message: Message, state: FSMContext):
    """Обработка кнопки возврата к поиску"""
    await message.answer(
        "✅ Можете продолжить поиск с текущими фильтрами",
        reply_markup=create_exact_search_keyboard()
    )
    await state.set_state(SearchStates.waiting_for_query)


@router.message(SearchStates.setting_countries)
async def handle_countries_input(message: Message, state: FSMContext):
    """Обработка ввода стран"""
    if message.text == "🔄 Вернуться к поиску":
        await handle_return_to_search(message, state)
        return

    countries = [c.strip().upper() for c in message.text.split(",")]
    await state.update_data(countries=countries)
    await show_current_filters(message, state)


@router.message(SearchStates.setting_ipc_codes)
async def handle_ipc_input(message: Message, state: FSMContext):
    """Обработка ввода кодов МПК"""
    if message.text == "🔄 Вернуться к поиску":
        await handle_return_to_search(message, state)
        return

    ipc_codes = [code.strip().upper() for code in message.text.split(",")]
    await state.update_data(ipc_codes=ipc_codes)
    await show_current_filters(message, state)


@router.message(SearchStates.setting_cpc_codes)
async def handle_cpc_input(message: Message, state: FSMContext):
    """Обработка ввода кодов СПК"""
    if message.text == "🔄 Вернуться к поиску":
        await handle_return_to_search(message, state)
        return

    cpc_codes = [code.strip().upper() for code in message.text.split(",")]
    await state.update_data(cpc_codes=cpc_codes)
    await show_current_filters(message, state)


@router.message(SearchStates.setting_date_from)
async def handle_date_from_input(message: Message, state: FSMContext):
    """Обработка ввода глубины поиска"""
    if message.text == "🔄 Вернуться к поиску":
        await handle_return_to_search(message, state)
        return

    try:
        years = int(message.text)
        if not 1 <= years <= 30:
            raise ValueError("Invalid years range")
            
        # Вычисляем дату начала поиска
        date_from = datetime.now().date() - timedelta(days=years*365)
        
        await state.update_data(date_from=date_from)
        await show_current_filters(message, state)
    
    except ValueError:
        await message.answer(
            "❌ Неверный формат. Введите число от 1 до 30.",
            reply_markup=create_exact_search_keyboard()
        )


async def show_current_filters(message: Message, state: FSMContext):
    """Отображение текущих фильтров"""
    data = await state.get_data()
    
    filter_text = "🔍 <b>Текущие фильтры:</b>\n\n"
    
    if countries := data.get('countries'):
        filter_text += f"🌍 <b>Страны:</b> {', '.join(countries)}\n"
    else:
        filter_text += "🌍 <b>Страны:</b> не выбраны\n"
    
    if ipc_codes := data.get('ipc_codes'):
        filter_text += f"📑 <b>Коды МПК:</b> {', '.join(ipc_codes)}\n"
    else:
        filter_text += "📑 <b>Коды МПК:</b> не выбраны\n"
    
    if cpc_codes := data.get('cpc_codes'):
        filter_text += f"📋 <b>Коды СПК:</b> {', '.join(cpc_codes)}\n"
    else:
        filter_text += "📋 <b>Коды СПК:</b> не выбраны\n"
    
    if date_from := data.get('date_from'):
        years_ago = (datetime.now().date() - date_from).days // 365
        filter_text += f"📅 <b>Глубина поиска:</b> {years_ago} лет\n"
    else:
        filter_text += "📅 <b>Глубина поиска:</b> не задана\n"

    await message.answer(
        filter_text,
        parse_mode="HTML",
        reply_markup=create_filter_keyboard()
    )
    await state.set_state(SearchStates.confirming_filters)


@router.callback_query(F.data == "reset_filters")
async def reset_filters(callback: CallbackQuery, state: FSMContext):
    """Сброс всех фильтров"""
    await state.update_data({
        'countries': None,
        'ipc_codes': None,
        'cpc_codes': None,
        'date_from': None,
        'date_to': None
    })
    await callback.answer("🔄 Фильтры сброшены")
    await show_current_filters(callback.message, state)


@router.callback_query(F.data == "apply_filters")
async def apply_filters(callback: CallbackQuery, state: FSMContext):
    """Применение фильтров и переход к поиску"""
    await callback.message.answer(
        "✅ Фильтры установлены. Теперь введите поисковый запрос:",
        reply_markup=create_exact_search_keyboard()
    )
    await state.set_state(SearchStates.waiting_for_query) 