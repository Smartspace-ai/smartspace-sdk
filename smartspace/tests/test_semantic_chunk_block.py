from unittest.mock import Mock, patch

import pytest

from smartspace.blocks.semantic_chunk import SemanticChunk


@pytest.fixture(scope="function")
def mock_block():
    return Mock(
        spec=SemanticChunk,
        buffer_size=1,
        breakpoint_percentile_threshold=95,
        chunk_model="BAAI/bge-small-en-v1.5",
    )


@pytest.mark.asyncio
async def test_chunk_empty_input(mock_block: Mock):
    mocked_chunk = SemanticChunk(Mock(), Mock())
    input_text = ""  # Create a short input text

    result = await mocked_chunk.semantic_chunk._fn(mock_block, input_text)

    assert isinstance(result, list)
    assert len(result) == 1


@pytest.mark.asyncio
async def test_chunk_long_input(mock_block: Mock):
    mocked_chunk = SemanticChunk(Mock(), Mock())
    input_text = (
        "This is a sample text for testing token chunking with custom configuration. "
        * 1000
    )  # Create a long input text

    result = await mocked_chunk.semantic_chunk._fn(mock_block, input_text)

    assert isinstance(result, list)
    assert len(result) > 0  # The result should contain at least one chunk
    assert all(isinstance(chunk, str) for chunk in result)


@pytest.mark.asyncio
async def test_chunk_with_list_input(mock_block: Mock):
    mocked_chunk = SemanticChunk(Mock(), Mock())
    input_texts = [
        "This is the first sample text. " * 100,
        "This is the second sample text for testing. " * 100,
    ]

    result = await mocked_chunk.semantic_chunk._fn(mock_block, input_texts)

    assert isinstance(result, list)
    assert len(result) > 0
    assert all(isinstance(chunk, str) for chunk in result)


@pytest.mark.asyncio
async def test_chunk_with_custom_config(mock_block: Mock):
    mock_block.buffer_size = 100
    mock_block.breakpoint_percentile_threshold = 5

    mocked_chunk = SemanticChunk(Mock(), Mock())
    input_text = (
        "This is a sample text for testing token chunking with custom configuration. "
        * 100
    )

    result = await mocked_chunk.semantic_chunk._fn(mock_block, input_text)

    assert isinstance(result, list)
    assert len(result) > 0
    assert all(isinstance(chunk, str) for chunk in result)


@pytest.mark.asyncio
async def test_chunk_error_handling(mock_block: Mock):
    mocked_chunk = SemanticChunk(Mock(), Mock())
    input_text = "This is a sample text. " * 100

    with patch(
        "llama_index.core.node_parser.SemanticSplitterNodeParser.get_nodes_from_documents",
        side_effect=Exception("Mocked error"),
    ):
        with pytest.raises(RuntimeError) as exc_info:
            await mocked_chunk.semantic_chunk._fn(mock_block, input_text)

        assert "Error during chunking" in str(exc_info.value)
