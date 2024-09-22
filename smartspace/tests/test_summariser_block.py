from unittest.mock import AsyncMock, Mock, patch

import pytest

from smartspace.blocks.summariser_block import Summariser
from smartspace.models import ContentItem, InMemorySearchResult


@pytest.fixture(scope="function")
def mock_block():
    mock = Mock(spec=Summariser)
    mock.llm_name = "HuggingFaceH4/tiny-random-LlamaForCausalLM"
    mock.tokenizer_name = "HuggingFaceH4/tiny-random-LlamaForCausalLM"
    mock.context_window = 4096
    mock.max_new_tokens = 256
    mock.temperature = 0.7
    mock.top_k = 50
    mock.top_p = 0.95
    return mock


@pytest.mark.asyncio
async def test_summarize_empty_input(mock_block: Mock):
    summariser = Summariser(Mock(), Mock())
    result = await summariser.summarize._fn(mock_block, [], [])
    assert result == [{"image": None, "text": "No message provided."}]


@pytest.mark.asyncio
async def test_summarize_missing_document_names(mock_block: Mock):
    summariser = Summariser(Mock(), Mock())
    documents = [
        InMemorySearchResult(
            file_name=None, content="test", chunk_content="test", score=1.0
        )
    ]
    message = [ContentItem(text="Summarize this")]
    result = await summariser.summarize._fn(mock_block, documents, message)
    assert result == [{"image": None, "text": "Document names are missing."}]


@pytest.mark.asyncio
async def test_summarize_missing_chunk_contents(mock_block: Mock):
    summariser = Summariser(Mock(), Mock())
    documents = [
        InMemorySearchResult(
            file_name="test.txt", content="test", chunk_content=None, score=1.0
        )
    ]
    message = [ContentItem(text="Summarize this")]
    result = await summariser.summarize._fn(mock_block, documents, message)
    assert result == [{"image": None, "text": "Document chunks are missing."}]


@pytest.mark.asyncio
async def test_summarize_full_document(mock_block: Mock):
    # Create a mock tokenizer with an encode method
    mock_tokenizer = Mock()
    mock_tokenizer.encode.return_value = [1, 2, 3, 4]
    mock_block.tokenizer = mock_tokenizer

    mock_summarize_full = AsyncMock()
    mock_summarize_full.return_value = "Summary of the document"
    mock_block._summarize_full = mock_summarize_full

    summariser = Summariser(Mock(), Mock())

    documents = [
        InMemorySearchResult(
            file_name="test.txt",
            content="Short content",
            chunk_content="Short content",
            score=1.0,
        )
    ]
    message = [ContentItem(text="Summarize this")]
    result = await summariser.summarize._fn(mock_block, documents, message)

    assert result == [{"image": None, "text": "Summary of the document"}]


@pytest.mark.asyncio
async def test_summarize_progressive(mock_block: Mock):
    mock_tokenizer = Mock()
    mock_tokenizer.encode.return_value = (mock_block.context_window + 1) * [1]
    mock_block.tokenizer = mock_tokenizer

    mock_summarize_full = AsyncMock()
    mock_summarize_full.return_value = "Progressive summary"
    mock_block._progressive_summarize = mock_summarize_full

    summariser = Summariser(Mock(), Mock())

    long_content = "Long content unit test" * 1000
    documents = [
        InMemorySearchResult(
            file_name="test.txt",
            content=long_content,
            chunk_content="Chunk content",
            score=1.0,
        )
    ]
    message = [ContentItem(text="Summarize this")]
    result = await summariser.summarize._fn(mock_block, documents, message)

    mock_summarize_full.assert_called_once_with(["Chunk content"])
    assert result == [{"image": None, "text": "Progressive summary"}]


@pytest.mark.asyncio
async def test_summarize_full(mock_block: Mock):
    summariser = Summariser(Mock(), Mock())
    content = "Test content"

    result = await summariser._summarize_full(content)

    # with patch.object(summariser.llm, "complete", return_value=Mock(text="Summary")):
    #     result = await summariser._summarize_full(content)

    assert len(result) > 0


@pytest.mark.asyncio
async def test_progressive_summarize(mock_block: Mock):
    summariser = Summariser(Mock(), Mock())
    chunks = ["Chunk 1", "Chunk 2", "Chunk 3"]

    with patch.object(
        summariser,
        "_summarize_full",
        side_effect=["Summary 1", "Summary 2", "Summary 3", "Final Summary"],
    ):
        result = await summariser._progressive_summarize(chunks)

    assert result == "Final Summary"
