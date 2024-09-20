from unittest.mock import patch

import pytest
from transformers import AutoTokenizer

from smartspace.blocks.sentence_chunk import SentenceChunk


@pytest.mark.asyncio
async def test_chunk_empty_input():
    mocked_chunk = SentenceChunk()
    input_text = ""  # Create a short input text

    result = await mocked_chunk.sentence_chunk(input_text)

    assert isinstance(result, list)
    assert len(result) == 1
    assert all(isinstance(chunk, str) for chunk in result)


@pytest.mark.asyncio
async def test_chunk_long_input():
    mocked_chunk = SentenceChunk()
    input_text = (
        "This is a sample text for testing token chunking with custom configuration."
        * 1000
    )  # Create a long input text

    result = await mocked_chunk.sentence_chunk(input_text)

    assert isinstance(result, list)
    assert len(result) > 1  # The result should contain at least one chunk
    assert all(isinstance(chunk, str) for chunk in result)


@pytest.mark.asyncio
async def test_chunk_with_list_input():
    mocked_chunk = SentenceChunk()
    input_texts = [
        "This is the first sample text." * 100,
        "This is the second sample text for testing." * 100,
    ]

    result = await mocked_chunk.sentence_chunk(input_texts)

    assert isinstance(result, list)
    assert len(result) > 1
    assert all(isinstance(chunk, str) for chunk in result)


@pytest.mark.asyncio
async def test_chunk_with_custom_config():
    mocked_chunk = SentenceChunk()
    mocked_chunk.chunk_size = 100
    mocked_chunk.chunk_overlap = 5
    mocked_chunk.separator = "|"
    mocked_chunk.paragraph_separator = (
        "\n"  # Change the separator，"\n" is a newline character
    )
    mocked_chunk.secondary_chunking_regex = (
        "[^,.]+[,.]?"  # new regex means split by comma or period
    )

    mocked_chunk.model_name = "HuggingFaceH4/zephyr-7b-beta"

    input_text = (
        "This is a sample text for testing token chunking with custom configuration."
        * 100
    )

    result = await mocked_chunk.sentence_chunk(input_text)

    assert isinstance(result, list)
    assert len(result) > 1
    assert all(isinstance(chunk, str) for chunk in result)


@pytest.mark.asyncio
async def test_chunk_error_handling():
    mocked_chunk = SentenceChunk()
    input_text = "This is a sample text." * 100

    with patch(
        "llama_index.core.node_parser.SentenceSplitter.get_nodes_from_documents",
        side_effect=Exception("Mocked error"),
    ):
        with pytest.raises(RuntimeError) as exc_info:
            await mocked_chunk.sentence_chunk(input_text)

        assert "Error during chunking" in str(exc_info.value)


@pytest.mark.asyncio
async def test_chunk_tokenizer_error_handling():
    mocked_chunk = SentenceChunk()
    mocked_chunk.model_name = "non_existent_model"
    input_text = "This is a sample text. "

    with patch.object(
        AutoTokenizer, "from_pretrained", side_effect=Exception("Tokenizer error")
    ):
        with pytest.raises(RuntimeError) as exc_info:
            await mocked_chunk.sentence_chunk(input_text)

        assert "Error loading tokenizer for model" in str(exc_info.value)
