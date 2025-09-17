# src/interfaces/telegram/utils/formatters.py

from typing import Any, List, Optional


def truncate_text(text: str, max_length: int = 4000) -> str:
    """Обрезает текст до указанной длины и добавляет многоточие"""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "...\n\n<i>Полный текст доступен по ссылке на патент</i>"


def format_patent_message(patent: Any, index: int, summary: Optional[dict] = None) -> List[str]:
    """Форматирование сообщения с информацией о патенте"""
    # Форматируем даты
    pub_date = "Не указана"
    if patent.publication_date:
        pub_date = patent.publication_date.strftime("%d.%m.%Y")
        
    app_date = "Не указана"
    if patent.application_date:
        app_date = patent.application_date.strftime("%d.%m.%Y")
    
    # Формируем ссылку на патент
    patent_link = f"https://searchplatform.rospatent.gov.ru/doc/{patent.id}"
    
    # Основная информация всегда будет в первом сообщении
    main_info = (
        f"🔎 <b>Патент #{index}</b>\n"
        f"📑 <b>Номер патента:</b> {patent.id}\n"
        f"🔗 <b>Ссылка:</b> {patent_link}\n"
        f"📑 <b>Название:</b> {patent.title}\n"
        f"📅 <b>Дата публикации:</b> {pub_date}\n"
        f"📅 <b>Дата подачи заявки:</b> {app_date}\n"
        f"👤 <b>Авторы:</b> {', '.join(patent.authors)}\n"
        f"💼 <b>Патентообладатели:</b> {', '.join(patent.patent_holders)}\n"
        f"🔰 <b>МПК:</b> {', '.join(patent.ipc_codes)}"
    )

    parts = [main_info]

    # Добавляем суммаризацию от GigaChat, если она есть
    if summary and summary.get("status") == "success":
        parts.append(f"🤖 <b>Анализ:</b>\n{summary['summary']}")
    else:
        # Если нет суммаризации, добавляем стандартную информацию
        if patent.abstract:
            parts.append(f"📝 <b>Реферат:</b>\n{truncate_text(patent.abstract)}")
        
        if patent.claims:
            parts.append(f"📋 <b>Формула изобретения:</b>\n{truncate_text(patent.claims)}")

    return parts