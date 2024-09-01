from unittest.mock import Mock

import pytest

from smartspace.blocks.regex_match import RegexMatch


@pytest.fixture
def mock_block():
    return Mock(
        spec=RegexMatch, regex=r".*"
    )  # Default pattern to match the entire string


@pytest.mark.asyncio
async def test_regex_match_default_pattern(mock_block):
    regex_block = RegexMatch(Mock(), Mock())
    input_string = "Hello, World!"
    result = await regex_block.regex_match._fn(mock_block, input_string)
    assert result == ["Hello, World!", ""]


@pytest.mark.asyncio
async def test_regex_match_custom_pattern(mock_block):
    mock_block.regex = r"\b\w+\b"  # Match words
    regex_block = RegexMatch(Mock(), Mock())
    input_string = "Hello, World! How are you?"
    result = await regex_block.regex_match._fn(mock_block, input_string)
    assert result == ["Hello", "World", "How", "are", "you"]


@pytest.mark.asyncio
async def test_regex_match_no_match(mock_block):
    mock_block.regex = r"\d+"  # Match numbers
    regex_block = RegexMatch(Mock(), Mock())
    input_string = "No numbers here"
    result = await regex_block.regex_match._fn(mock_block, input_string)
    assert result == ["No match found"]


@pytest.mark.asyncio
async def test_regex_match_invalid_pattern(mock_block):
    mock_block.regex = r"["  # Invalid regex pattern
    regex_block = RegexMatch(Mock(), Mock())
    input_string = "Test string"
    result = await regex_block.regex_match._fn(mock_block, input_string)
    assert result[0].startswith("Error: ")


@pytest.mark.asyncio
async def test_regex_match_empty_input(mock_block):
    regex_block = RegexMatch(Mock(), Mock())
    input_string = ""
    result = await regex_block.regex_match._fn(mock_block, input_string)
    assert result == [""]


@pytest.mark.asyncio
async def test_regex_match_multiple_matches(mock_block):
    mock_block.regex = r"\b\w{3}\b"  # Match 3-letter words
    regex_block = RegexMatch(Mock(), Mock())
    input_string = "The cat and dog are pets"
    result = await regex_block.regex_match._fn(mock_block, input_string)
    assert result == ["The", "cat", "and", "dog", "are"]
