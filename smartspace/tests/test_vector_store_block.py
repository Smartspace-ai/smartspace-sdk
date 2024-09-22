from unittest.mock import Mock

import pytest
from qdrant_client import QdrantClient
from qdrant_client.models import ScoredPoint

from smartspace.blocks.vector_store_block import VectorStore
from smartspace.models import InMemorySearchResult


@pytest.fixture(scope="function")
def mock_block():
    return Mock(
        spec=VectorStore,
        top_k=5,
        client=Mock(spec=QdrantClient),
        files=[],
        embedding_size=0,
    )


@pytest.mark.asyncio
async def test_create_store_new_collection(mock_block: Mock):
    vector_store = VectorStore(Mock(), Mock())
    filecontent = "Test content"
    filename = "test.txt"
    chunk_positions = [(0, 5), (6, 11)]
    chunk_embeddings = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]

    await vector_store.create_store._fn(
        mock_block, filecontent, filename, chunk_positions, chunk_embeddings
    )

    assert mock_block.embedding_size == 3
    mock_block.client.recreate_collection.assert_called_once()
    mock_block.client.upsert.assert_called_once()
    assert len(mock_block.files) == 1


@pytest.mark.asyncio
async def test_create_store_existing_collection(mock_block: Mock):
    mock_block.embedding_size = 3
    vector_store = VectorStore(Mock(), Mock())
    filecontent = "Test content"
    filename = "test.txt"
    chunk_positions = [(0, 5), (6, 11)]
    chunk_embeddings = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]

    await vector_store.create_store._fn(
        mock_block, filecontent, filename, chunk_positions, chunk_embeddings
    )

    mock_block.client.recreate_collection.assert_not_called()
    mock_block.client.upsert.assert_called_once()
    assert len(mock_block.files) == 1


@pytest.mark.asyncio
async def test_create_store_inconsistent_embedding_size(mock_block: Mock):
    mock_block.embedding_size = 3
    vector_store = VectorStore(Mock(), Mock())
    filecontent = "Test content"
    filename = "test.txt"
    chunk_positions = [(0, 5), (6, 11)]
    chunk_embeddings = [[0.1, 0.2, 0.3, 0.4], [0.4, 0.5, 0.6, 0.7]]

    with pytest.raises(ValueError, match="The embedding size should be consistent"):
        await vector_store.create_store._fn(
            mock_block, filecontent, filename, chunk_positions, chunk_embeddings
        )


@pytest.mark.asyncio
async def test_search_empty_store(mock_block: Mock):
    vector_store = VectorStore(Mock(), Mock())
    query_embedding = [[0.1, 0.2, 0.3]]

    result = await vector_store.search._fn(mock_block, query_embedding)

    assert result == []


@pytest.mark.asyncio
async def test_search_with_results(mock_block: Mock):
    vector_store = VectorStore(Mock(), Mock())
    mock_block.files = [
        {
            "filecontent": "Test content",
            "filename": "test.txt",
            "chunk_names": ["test.txt_chunk_0"],
            "chunk_positions": [(0, 5)],
        }
    ]
    query_embedding = [[0.1, 0.2, 0.3]]

    mock_search_result = ScoredPoint(
        id=0,
        version=1,
        score=0.9,
        payload={
            "filename": "test.txt",
            "chunk_name": "test.txt_chunk_0",
            "chunk_position": (0, 5),
        },
        vector=None,
    )
    mock_block.client.search.return_value = [mock_search_result]

    result = await vector_store.search._fn(mock_block, query_embedding)

    assert len(result) == 1
    assert isinstance(result[0], InMemorySearchResult)
    assert result[0].file_name == "test.txt"
    assert result[0].content == "Test content"
    assert result[0].chunk_content == "Test "
    assert result[0].score == 0.9


@pytest.mark.asyncio
async def test_search_empty_payload(mock_block: Mock):
    vector_store = VectorStore(Mock(), Mock())
    mock_block.files = [
        {
            "filecontent": "Test content",
            "filename": "test.txt",
            "chunk_names": ["test.txt_chunk_0"],
            "chunk_positions": [(0, 5)],
        }
    ]
    query_embedding = [[0.1, 0.2, 0.3]]

    mock_search_result = ScoredPoint(
        id=0, version=1, score=0.9, payload=None, vector=None
    )
    mock_block.client.search.return_value = [mock_search_result]

    with pytest.raises(ValueError, match="Payload is empty"):
        await vector_store.search._fn(mock_block, query_embedding)
