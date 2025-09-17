# tests/unit/test_repository.py

from datetime import date
from unittest.mock import AsyncMock

import pytest
import responses

from src.domain.entities.patent import Patent
from src.infrastructure.rospatent.config import RospatentConfig
from src.infrastructure.rospatent.repository import RospatentRepository


@pytest.fixture
def config():
    return RospatentConfig(jwt_token="test_jwt")


@responses.activate
@pytest.mark.asyncio
async def test_search_by_query(config):
    repository = RospatentRepository(config)

    # Мокаем запрос поиска патентов
    responses.add(
        responses.POST,
        "https://searchplatform.rospatent.gov.ru/patsearch/v0.2/search",
        json={
            "hits": [
                {"id": "123"}
            ]
        },
        status=200,
        headers={"Content-Type": "application/json"}
    )

    # Мокаем запрос получения деталей патента
    responses.add(
        responses.GET,
        "https://searchplatform.rospatent.gov.ru/patsearch/v0.2/docs/123",
        json={
            "common": {
                "publication_date": "2023-01-01",
                "application": {"filing_date": "2022-01-01"},
                "classification": {"ipc": [{"fullname": "IPC1"}]}
            },
            "biblio": {
                "ru": {
                    "title": "Test Patent",
                    "inventor": [{"name": "Author A"}],
                    "patentee": [{"name": "Holder A"}]
                }
            },
            "abstract": {"ru": "Abstract"},
            "claims": {"ru": "Claims"},
            "description": {"ru": "Description"}
        },
        status=200,
        headers={"Content-Type": "application/json"}
    )

    result = await repository.search_by_query("Test Query", limit=1)

    assert len(result) == 1
    patent = result[0]
    assert patent.id == "123"
    assert patent.title == "Test Patent"
    assert patent.publication_date == date(2023, 1, 1)
    assert patent.application_date == date(2022, 1, 1)
    assert patent.authors == ["Author A"]
    assert patent.patent_holders == ["Holder A"]
    assert patent.ipc_codes == ["IPC1"]
    assert patent.abstract == "Abstract"
    assert patent.claims == "Claims"
    assert patent.description == "Description"


@responses.activate
@pytest.mark.asyncio
async def test_get_by_id_not_found(config):
    repository = RospatentRepository(config)

    # Мокаем запрос получения несуществующего патента
    responses.add(
        responses.GET,
        "https://searchplatform.rospatent.gov.ru/patsearch/v0.2/docs/999",
        status=404
    )

    result = await repository.get_by_id("999")
    assert result is None
