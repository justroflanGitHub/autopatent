# tests/unit/test_patent_search.py

from unittest.mock import AsyncMock

import pytest

from src.application.use_cases.patent_search import PatentSearchUseCase
from src.domain.repositories.patent_repository import PatentRepository


@pytest.mark.asyncio
async def test_search_by_query():
    # Arrange
    mock_repo = AsyncMock(spec=PatentRepository)
    use_case = PatentSearchUseCase(mock_repo)
    query = "Test Query"
    expected_patents = [AsyncMock()]
    mock_repo.search_by_query = AsyncMock(return_value=expected_patents)

    # Act
    result = await use_case.search_by_query(query)

    # Assert
    mock_repo.search_by_query.assert_awaited_once_with(query, 10, None)
    assert result.query == query
    assert result.total_count == len(expected_patents)
    assert result.patents == expected_patents


@pytest.mark.asyncio
async def test_search_by_query_with_empty_result():
    # Arrange
    mock_repo = AsyncMock(spec=PatentRepository)
    use_case = PatentSearchUseCase(mock_repo)
    query = "Non-existent Query"
    mock_repo.search_by_query = AsyncMock(return_value=[])

    # Act
    result = await use_case.search_by_query(query)

    # Assert
    mock_repo.search_by_query.assert_awaited_once_with(query, 10, None)
    assert result.query == query
    assert result.total_count == 0
    assert result.patents == []