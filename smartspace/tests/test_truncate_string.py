from unittest.mock import patch

import pytest

from smartspace.blocks.truncate_string import StringTruncator


@pytest.mark.asyncio
async def test_truncate_string_no_truncation_needed():
    truncator = StringTruncator()
    input_string = "This is a short string that doesn't need truncation."

    with patch("smartspace.blocks.truncate_string.encode") as mock_encode:
        mock_encode.return_value = [1] * 50  # Simulate 50 tokens
        result = await truncator.truncate_string(input_string)

    assert result == input_string


@pytest.mark.asyncio
async def test_truncate_string_truncation_needed():
    truncator = StringTruncator()
    input_string = "This is a long string that needs truncation." * 10

    with (
        patch("smartspace.blocks.truncate_string.encode") as mock_encode,
        patch("smartspace.blocks.truncate_string.decode") as mock_decode,
    ):
        mock_encode.return_value = [1] * 150  # Simulate 150 tokens
        mock_decode.return_value = "This is a truncated string."
        result = await truncator.truncate_string(input_string)

    assert result == "This is a truncated string."
    mock_encode.assert_called_once_with(model=truncator.model_name, text=input_string)
    mock_decode.assert_called_once_with(model=truncator.model_name, tokens=[1] * 100)


@pytest.mark.asyncio
async def test_truncate_string_custom_token_limit():
    truncator = StringTruncator()
    truncator.max_token = 50
    input_string = "This string should be truncated to a custom token limit."

    with (
        patch("smartspace.blocks.truncate_string.encode") as mock_encode,
        patch("smartspace.blocks.truncate_string.decode") as mock_decode,
    ):
        mock_encode.return_value = [1] * 75  # Simulate 75 tokens
        mock_decode.return_value = "This string should be truncated to a custom"
        result = await truncator.truncate_string(input_string)

    assert result == "This string should be truncated to a custom"
    mock_decode.assert_called_once_with(model=truncator.model_name, tokens=[1] * 50)


@pytest.mark.asyncio
async def test_truncate_string_custom_model():
    truncator = StringTruncator()
    truncator.model_name = "gpt-4"
    input_string = "This string uses a different model for encoding and decoding."

    with (
        patch("smartspace.blocks.truncate_string.encode") as mock_encode,
        patch("smartspace.blocks.truncate_string.decode") as mock_decode,
    ):
        mock_encode.return_value = [1] * 180  # Simulate 80 tokens
        mock_decode.return_value = "This string uses a different model for encoding"
        result = await truncator.truncate_string(input_string)

    assert result == "This string uses a different model for encoding"
    mock_encode.assert_called_once_with(model="gpt-4", text=input_string)
    mock_decode.assert_called_once_with(model="gpt-4", tokens=[1] * truncator.max_token)


@pytest.mark.asyncio
async def test_truncate_string_empty_input():
    truncator = StringTruncator()
    input_string = ""

    with patch("smartspace.blocks.truncate_string.encode") as mock_encode:
        mock_encode.return_value = []  # Simulate 0 tokens
        result = await truncator.truncate_string(input_string)

    assert result == ""


@pytest.mark.asyncio
async def test_truncate_string_exact_token_limit():
    truncator = StringTruncator()
    input_string = "This string has exactly the token limit."

    with patch("smartspace.blocks.truncate_string.encode") as mock_encode:
        mock_encode.return_value = [1] * 100  # Simulate exactly 100 tokens
        result = await truncator.truncate_string(input_string)

    assert result == input_string
