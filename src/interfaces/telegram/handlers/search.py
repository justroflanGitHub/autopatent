# src/interfaces/telegram/handlers/search.py

import logging
from typing import Optional

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile, Message

from src.application.services.patent_summarizer import PatentSummarizer
from src.application.use_cases.patent_search import PatentSearchUseCase
from src.domain.entities.search_filter import SearchFilter
from src.infrastructure.cache.patent_cache import PatentCache
from src.infrastructure.utils.text import count_words
from src.interfaces.telegram.keyboards.filters import create_filter_keyboard
from src.interfaces.telegram.keyboards.main import (
    create_exact_search_keyboard,
    create_main_keyboard,
)
from src.interfaces.telegram.states.search import SearchStates
from src.interfaces.telegram.utils.document import create_search_results_doc
from src.interfaces.telegram.utils.formatters import format_patent_message

logger = logging.getLogger(__name__)

router = Router()


class SearchHandler:
    """Обработчик поисковых запросов"""

    def __init__(
        self,
        search_use_case: PatentSearchUseCase,
        patent_summarizer: PatentSummarizer,
        patent_cache: PatentCache
    ):
        self.search_use_case = search_use_case
        self.patent_summarizer = patent_summarizer
        self.patent_cache = patent_cache
        self._register_handlers()

    def _register_handlers(self) -> None:
        """Регистрация обработчиков"""
        router.message.register(self.cmd_start, Command("start"))
        router.message.register(self.cmd_help, Command("help"))
        
        # Регистрируем обработчики кнопок
        router.message.register(
            self.process_search_similar,
            F.text == "🔍 Семантический поиск"
        )
        router.message.register(
            self.process_search_exact,
            F.text == "🎯 Точный поиск"
        )
        router.message.register(
            self.process_filters_button,
            F.text == "⚙️ Настроить фильтры"
        )
        router.message.register(
            self.process_show_filters,
            F.text == "👁 Текущие фильтры"
        )
        router.message.register(
            self.process_return_to_main,
            F.text == "🔄 Вернуться в главное меню"
        )
        router.message.register(
            self.process_help_button,
            F.text == "❓ Помощь"
        )
        router.message.register(
            self.handle_search_query,
            SearchStates.waiting_for_query
        )

    async def cmd_start(self, message: Message, state: FSMContext) -> None:
        """Обработка команды /start"""
        logger.info(f"Получена команда /start от пользователя {message.from_user.id}")
        await message.answer(
            "👋 Привет! Я бот для поиска патентов. Выберите метод поиска:",
            reply_markup=create_main_keyboard()
        )
        await state.set_state(SearchStates.choosing_method)

    async def cmd_help(self, message: Message) -> None:
        """Обработка команды /help"""
        await message.answer(
            "ℹ️ Я могу помочь вам найти патенты по двум методам:\n\n"
            "**🔍 Семантический поиск**: Поиск патентов, похожих по смыслу "
            "на ваше описание.\n"
            "**🎯 Точный поиск**: Поиск патентов по конкретным ключевым словам.\n\n"
            "Используйте кнопки ниже для выбора метода поиска.",
            reply_markup=create_main_keyboard(),
            parse_mode="Markdown"
        )

    async def process_search_similar(
        self,
        message: Message,
        state: FSMContext
    ) -> None:
        """Обработка выбора семантического поиска"""
        await message.answer(
            "🔍 <b>Семантический поиск</b> выбран.\n\n"
            "❗️ Для получения релевантных результатов необходимо ввести "
            "подробное описание (минимум 50 слов).\n\n"
            "✍️ Пожалуйста, введите ваш запрос:",
            parse_mode="HTML",
            reply_markup=create_main_keyboard()
        )
        await state.update_data(search_method="semantic")
        await state.set_state(SearchStates.waiting_for_query)

    async def process_search_exact(
        self,
        message: Message,
        state: FSMContext
    ) -> None:
        """Обработка выбора точного поиска"""
        await state.update_data(search_method="exact")
        
        # Отправляем основное сообщение с инструкциями
        await message.answer(
            "🎯 *Точный поиск* выбран.\n\n"
            "Введите поисковый запрос или воспользуйтесь дополнительными опциями:",
            parse_mode="Markdown",
            reply_markup=create_exact_search_keyboard()
        )
        
        await state.set_state(SearchStates.waiting_for_query)

    async def process_filters_button(
        self,
        message: Message,
        state: FSMContext
    ) -> None:
        """Обработка нажатия кнопки настройки фильтров"""
        data = await state.get_data()
        if data.get('search_method') != "exact":
            return
            
        await message.answer(
            "⚙️ Настройка фильтров поиска:",
            reply_markup=create_filter_keyboard()
        )
        await state.set_state(SearchStates.confirming_filters)

    async def process_show_filters(
        self,
        message: Message,
        state: FSMContext
    ) -> None:
        """Обработка нажатия кнопки просмотра текущих фильтров"""
        data = await state.get_data()
        if data.get('search_method') != "exact":
            return
            
        search_filter = self._create_search_filter(data)
        filter_info = self._format_filter_info(search_filter)
        
        await message.answer(
            f"🔍 <b>Текущие настройки поиска:</b>\n\n{filter_info}",
            parse_mode="HTML",
            reply_markup=create_exact_search_keyboard()
        )

    async def process_return_to_main(
        self,
        message: Message,
        state: FSMContext
    ) -> None:
        """Обработка возврата в главное меню"""
        await state.clear()
        await message.answer(
            "Выберите режим поиска:",
            reply_markup=create_main_keyboard()
        )
        await state.set_state(SearchStates.choosing_method)

    async def process_help_button(self, message: Message) -> None:
        """Обработка нажатия кнопки помощи"""
        await self.cmd_help(message)

    async def handle_search_query(
        self,
        message: Message,
        state: FSMContext
    ) -> None:
        """Обработка поискового запроса"""
        # Пропускаем обработку специальных команд
        if message.text.startswith('/') or message.text in [
            "⚙️ Настроить фильтры",
            "👁 Текущие фильтры",
            "🔄 Вернуться в главное меню"
        ]:
            return

        data = await state.get_data()
        method = data.get('search_method')
        query = message.text

        # Проверка длины запроса для семантического поиска
        if method == "semantic" and count_words(query) < 50:
            await message.answer(
                "⚠️ <b>Для семантического поиска необходимо ввести не менее 50 слов.</b>\n\n"
                "Пожалуйста, предоставьте более подробное описание для получения релевантных результатов.",
                parse_mode="HTML",
                reply_markup=create_main_keyboard()
            )
            return

        # Отправляем сообщение о начале поиска
        await message.answer(
            "🔍 <b>Идет поиск и анализ патентов, подождите немного...</b>",
            parse_mode="HTML"
        )

        try:
            # Создаем объект фильтра из сохраненных данных
            search_filter = self._create_search_filter(data)

            if method == "semantic":
                result = await self.search_use_case.search_similar(query)
            else:
                result = await self.search_use_case.search_by_query(
                    query,
                    search_filter=search_filter
                )

            if result.patents:
                # Формируем сообщение с примененными фильтрами только для точного поиска
                message_text = f"✨ <b>Найдено патентов:</b> {result.total_count}"
                if method == "exact":
                    filter_info = self._format_filter_info(search_filter)
                    message_text += f"\n\n{filter_info}"
                
                await message.answer(
                    message_text,
                    parse_mode="HTML"
                )

                # Собираем анализы для всех патентов
                await message.answer(
                    "⏳ Выполняется анализ найденных патентов и формирование документа...",
                    parse_mode="HTML"
                )
                
                summaries = []
                for patent in result.patents:
                    analysis = await self.patent_summarizer.analyze_patent(
                        patent.id,
                        patent.get_full_text()
                    )
                    summaries.append(
                        {"status": "success", "summary": analysis} if analysis else None
                    )
                
                # Создаем документ с результатами
                filename = create_search_results_doc(result.patents, summaries)
                
                # Отправляем документ
                doc = FSInputFile(filename)
                await message.answer_document(
                    doc,
                    caption="📄 Результаты поиска в формате DOC"
                )
                
                # Удаляем временный файл
                import os
                os.remove(filename)

            else:
                await message.answer(
                    "❌ Патенты не найдены. Попробуйте изменить запрос или фильтры.",
                    reply_markup=create_main_keyboard()
                )

        except Exception as e:
            import traceback
            logger.error(f"Ошибка при обработке запроса: {repr(e)}\n{traceback.format_exc()}")
            await message.answer(
                "❌ Произошла ошибка при обработке запроса"
            )

        # В конце поиска возвращаем соответствующую клавиатуру
        data = await state.get_data()
        keyboard = (
            create_exact_search_keyboard()
            if data.get('search_method') == "exact"
            else create_main_keyboard()
        )
        
        await message.answer(
            "✍️ Введите новый запрос или выберите другое действие:",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        
        # Сохраняем состояние для следующего запроса
        await state.set_state(SearchStates.waiting_for_query)

    def _create_search_filter(self, data: dict) -> Optional[SearchFilter]:
        """Создание объекта SearchFilter из данных состояния"""
        if not any([
            data.get('countries'),
            data.get('ipc_codes'),
            data.get('cpc_codes'),
            data.get('date_from'),
            data.get('date_to')
        ]):
            return None

        return SearchFilter(
            countries=data.get('countries'),
            ipc_codes=data.get('ipc_codes'),
            cpc_codes=data.get('cpc_codes'),
            date_from=data.get('date_from'),
            date_to=data.get('date_to')
        )

    def _format_filter_info(self, search_filter: Optional[SearchFilter]) -> str:
        """Форматирование информации о примененных фильтрах"""
        if not search_filter:
            return "<i>Фильтры не применены</i>"

        filter_info = "<b>Применены фильтры:</b>\n"
        if search_filter.countries:
            filter_info += f"🌍 Страны: {', '.join(search_filter.countries)}\n"
        if search_filter.ipc_codes:
            filter_info += f"📑 МПК: {', '.join(search_filter.ipc_codes)}\n"
        if search_filter.cpc_codes:
            filter_info += f"📋 СПК: {', '.join(search_filter.cpc_codes)}\n"
        if search_filter.date_from:
            filter_info += f"📅 С: {search_filter.date_from.strftime('%d.%m.%Y')}\n"
        if search_filter.date_to:
            filter_info += f"📅 По: {search_filter.date_to.strftime('%d.%m.%Y')}\n"
        
        return filter_info