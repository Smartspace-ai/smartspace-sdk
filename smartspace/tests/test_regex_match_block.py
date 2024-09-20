import pytest

from smartspace.blocks.regex_match import RegexMatch


@pytest.mark.asyncio
async def test_regex_match_default_pattern():
    regex_block = RegexMatch()
    input_string = "Hello, World!"
    result = await regex_block.regex_match(input_string)
    assert result == ["Hello, World!", ""]


@pytest.mark.asyncio
async def test_regex_match_custom_pattern():
    regex_block = RegexMatch()
    regex_block.regex = r"\b\w+\b"  # Match words
    input_string = "Hello, World! How are you?"
    result = await regex_block.regex_match(input_string)
    assert result == ["Hello", "World", "How", "are", "you"]


@pytest.mark.asyncio
async def test_regex_match_no_match():
    regex_block = RegexMatch()
    regex_block.regex = r"\d+"  # Match numbers
    input_string = "No numbers here"
    result = await regex_block.regex_match(input_string)
    assert result == ["No match found"]


@pytest.mark.asyncio
async def test_regex_match_invalid_pattern():
    regex_block = RegexMatch()
    regex_block.regex = r"["  # Invalid regex pattern
    input_string = "Test string"
    result = await regex_block.regex_match(input_string)
    assert result[0].startswith("Error: ")


@pytest.mark.asyncio
async def test_regex_match_empty_input():
    regex_block = RegexMatch()
    input_string = ""
    result = await regex_block.regex_match(input_string)
    assert result == [""]


@pytest.mark.asyncio
async def test_regex_match_multiple_matches():
    regex_block = RegexMatch()
    regex_block.regex = r"\b\w{3}\b"  # Match 3-letter words
    input_string = "The cat and dog are pets"
    result = await regex_block.regex_match(input_string)
    assert result == ["The", "cat", "and", "dog", "are"]
