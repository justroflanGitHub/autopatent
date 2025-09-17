# tests/unit/test_formatters.py

from datetime import date

from src.domain.entities.patent import Patent
from src.interfaces.telegram.utils.formatters import (
    format_patent_message,
    truncate_text,
)


def test_truncate_text():
    long_text = "a" * 5000
    truncated = truncate_text(long_text, max_length=4000)
    assert len(truncated) == 4000 + len("...\n\n<i>Полный текст доступен по ссылке на патент</i>")
    assert truncated.endswith("...\n\n<i>Полный текст доступен по ссылке на патент</i>")

    short_text = "Short text"
    assert truncate_text(short_text, max_length=4000) == short_text


def test_format_patent_message():
    patent = Patent(
        id="123",
        title="Test Patent",
        publication_date=date(2023, 1, 1),
        application_date=date(2022, 1, 1),
        authors=["Author A"],
        patent_holders=["Holder A"],
        ipc_codes=["IPC1"],
        abstract="Abstract",
        claims="Claims",
        description="Description"
    )

    # Тест без summary (должен вернуть 3 сообщения: основное, реферат и формула)
    messages = format_patent_message(patent, index=1)
    assert len(messages) == 3

    main_info = messages[0]
    assert "🔎 <b>Патент #1</b>" in main_info
    assert "📑 <b>Номер патента:</b> 123" in main_info
    assert "🔗 <b>Ссылка:</b> https://searchplatform.rospatent.gov.ru/doc/123" in main_info
    assert "📑 <b>Название:</b> Test Patent" in main_info
    assert "📅 <b>Дата публикации:</b> 01.01.2023" in main_info
    assert "📅 <b>Дата подачи заявки:</b> 01.01.2022" in main_info
    assert "👤 <b>Авторы:</b> Author A" in main_info
    assert "💼 <b>Патентообладатели:</b> Holder A" in main_info
    assert "🔰 <b>МПК:</b> IPC1" in main_info

    assert "📝 <b>Реферат:</b>\nAbstract" in messages[1]
    assert "📋 <b>Формула изобретения:</b>\nClaims" in messages[2]

    # Тест с успешным summary (должен вернуть 2 сообщения: основное и анализ)
    messages_with_summary = format_patent_message(
        patent, 
        index=1, 
        summary={"status": "success", "summary": "Test analysis"}
    )
    assert len(messages_with_summary) == 2
    assert "🤖 <b>Анализ:</b>\nTest analysis" in messages_with_summary[1]

    # Тест с неуспешным summary (должен вернуть 3 сообщения как без summary)
    messages_with_failed_summary = format_patent_message(
        patent, 
        index=1, 
        summary={"status": "error", "summary": None}
    )
    assert len(messages_with_failed_summary) == 3