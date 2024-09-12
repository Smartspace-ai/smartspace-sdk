from unittest.mock import Mock, patch

import pytest
from transformers import AutoTokenizer

from smartspace.blocks.sentence_chunk import SentenceChunk


@pytest.fixture(scope="function")
def mock_block():
    return Mock(
        spec=SentenceChunk,
        chunk_size=200,
        chunk_overlap=10,
        separator=" ",
        paragraph_separator="\n\n\n",
        secondary_chunking_regex="[^,.;]+[,.;]?",
        model_name="gpt-3.5-turbo",
    )


@pytest.mark.asyncio
async def test_chunk_empty_input(mock_block: Mock):
    mocked_chunk = SentenceChunk(Mock(), Mock())
    input_text = ""  # Create a short input text

    result = await mocked_chunk.sentence_chunk._fn(mock_block, input_text)

    assert isinstance(result, list)
    assert len(result) == 1
    assert all(isinstance(chunk, str) for chunk in result)


@pytest.mark.asyncio
async def test_chunk_long_input(mock_block: Mock):
    mocked_chunk = SentenceChunk(Mock(), Mock())
    input_text = (
        "This is a sample text for testing token chunking with custom configuration."
        * 1000
    )  # Create a long input text

    result = await mocked_chunk.sentence_chunk._fn(mock_block, input_text)

    assert isinstance(result, list)
    assert len(result) > 1  # The result should contain at least one chunk
    assert all(isinstance(chunk, str) for chunk in result)


@pytest.mark.asyncio
async def test_chunk_with_list_input(mock_block: Mock):
    mocked_chunk = SentenceChunk(Mock(), Mock())
    input_texts = [
        "This is the first sample text." * 100,
        "This is the second sample text for testing." * 100,
    ]

    result = await mocked_chunk.sentence_chunk._fn(mock_block, input_texts)

    assert isinstance(result, list)
    assert len(result) > 1
    assert all(isinstance(chunk, str) for chunk in result)


@pytest.mark.asyncio
async def test_chunk_with_custom_config(mock_block: Mock):
    mock_block.chunk_size = 100
    mock_block.chunk_overlap = 5
    mock_block.separator = "|"
    mock_block.paragraph_separator = (
        "\n"  # Change the separator，"\n" is a newline character
    )
    mock_block.secondary_chunking_regex = (
        "[^,.]+[,.]?"  # new regex means split by comma or period
    )

    mock_block.model_name = "HuggingFaceH4/zephyr-7b-beta"

    mocked_chunk = SentenceChunk(Mock(), Mock())
    input_text = (
        "This is a sample text for testing token chunking with custom configuration."
        * 100
    )

    result = await mocked_chunk.sentence_chunk._fn(mock_block, input_text)

    assert isinstance(result, list)
    assert len(result) > 1
    assert all(isinstance(chunk, str) for chunk in result)


@pytest.mark.asyncio
async def test_chunk_error_handling(mock_block: Mock):
    mocked_chunk = SentenceChunk(Mock(), Mock())
    input_text = "This is a sample text." * 100

    with patch(
        "llama_index.core.node_parser.SentenceSplitter.get_nodes_from_documents",
        side_effect=Exception("Mocked error"),
    ):
        with pytest.raises(RuntimeError) as exc_info:
            await mocked_chunk.sentence_chunk._fn(mock_block, input_text)

        assert "Error during chunking" in str(exc_info.value)


@pytest.mark.asyncio
async def test_chunk_tokenizer_error_handling(mock_block: Mock):
    mock_block.model_name = "non_existent_model"
    mocked_chunk = SentenceChunk(Mock(), Mock())
    input_text = "This is a sample text. "

    with patch.object(
        AutoTokenizer, "from_pretrained", side_effect=Exception("Tokenizer error")
    ):
        with pytest.raises(RuntimeError) as exc_info:
            await mocked_chunk.sentence_chunk._fn(mock_block, input_text)

        assert "Error loading tokenizer for model" in str(exc_info.value)
