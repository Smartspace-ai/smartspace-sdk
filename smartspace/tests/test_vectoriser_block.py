from unittest.mock import Mock

import pytest
from qdrant_client.models import ScoredPoint

from smartspace.blocks.vector_store_block import VectorStore
from smartspace.models import InMemorySearchResult


@pytest.fixture
def mock_qdrant_client():
    mock = Mock()
    mock.search.return_value = [
        ScoredPoint(
            id=1,
            version=1,
            score=0.9,
            payload={
                "filename": "test.txt",
                "chunk_name": "test.txt_chunk_0",
                "chunk_position": (0, 100),
            },
            vector=None,
        )
    ]
    return mock


@pytest.fixture
def vector_store(mock_qdrant_client):
    store = VectorStore(Mock(), Mock())
    store.client = mock_qdrant_client
    store.files = [
        {
            "filecontent": "This is a test file content.",
            "filename": "test.txt",
            "chunk_names": ["test.txt_chunk_0"],
            "chunk_positions": [(0, 100)],
        }
    ]
    store.embedding_size = 128
    return store


@pytest.mark.asyncio
async def test_create_store(vector_store, mock_qdrant_client):
    await vector_store.create_store._fn(
        vector_store,
        filecontent="This is a test file content.",
        filename="test.txt",
        chunk_positions=[(0, 100)],
        chunk_embeddings=[[0.1] * 128],
    )

    assert len(vector_store.files) == 2
    mock_qdrant_client.upsert.assert_called_once()


@pytest.mark.asyncio
async def test_search(vector_store, mock_qdrant_client):
    query_embedding = [[0.1] * 128]

    results = await vector_store.search._fn(vector_store, query_embedding)

    assert isinstance(results, list)
    assert len(results) == 1
    assert isinstance(results[0], InMemorySearchResult)
    assert results[0].file_name == "test.txt"
    assert results[0].content == "This is a test file content."
    assert results[0].chunk_content == "This is a test file content."
    assert results[0].score == 0.9


@pytest.mark.asyncio
async def test_search_empty_store(vector_store):
    vector_store.files = []
    query_embedding = [[0.1] * 128]

    results = await vector_store.search._fn(vector_store, query_embedding)

    assert isinstance(results, list)
    assert len(results) == 0


@pytest.mark.asyncio
async def test_create_store_inconsistent_embedding_size(vector_store):
    with pytest.raises(ValueError, match="The embedding size should be consistent"):
        await vector_store.create_store._fn(
            vector_store,
            filecontent="This is another test file content.",
            filename="test2.txt",
            chunk_positions=[(0, 100)],
            chunk_embeddings=[[0.1] * 64],  # Inconsistent embedding size
        )
