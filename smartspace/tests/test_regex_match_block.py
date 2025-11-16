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


@pytest.mark.asyncio
async def test_regex_replace_basic():
    regex_block = RegexMatch()
    regex_block.regex = r"\d+"
    regex_block.replace_with = "X"
    input_string = "abc123def45"
    result = await regex_block.regex_match(input_string)
    assert result == "abcXdefX"


@pytest.mark.asyncio
async def test_regex_replace_no_match_returns_original():
    regex_block = RegexMatch()
    regex_block.regex = r"\d+"
    regex_block.replace_with = "X"
    input_string = "no digits here"
    result = await regex_block.regex_match(input_string)
    assert result == input_string


@pytest.mark.asyncio
async def test_regex_replace_invalid_pattern_returns_error_string():
    regex_block = RegexMatch()
    regex_block.regex = r"["  # Invalid pattern
    regex_block.replace_with = "X"
    input_string = "abc"
    result = await regex_block.regex_match(input_string)
    assert isinstance(result, str)
    assert result.startswith("Error: ")


@pytest.mark.asyncio
async def test_regex_replace_with_capturing_groups():
    regex_block = RegexMatch()
    regex_block.regex = r"(\d+)"
    regex_block.replace_with = r"[\1]"
    input_string = "a12b3"
    result = await regex_block.regex_match(input_string)
    assert result == "a[12]b[3]"


@pytest.mark.asyncio
async def test_mode_switch_match_then_replace_then_match():
    input_string = "Hi 42"

    # Match mode (default replace_with is empty) - new instance
    regex_block_match_1 = RegexMatch()
    regex_block_match_1.regex = r"\w+"
    result_match = await regex_block_match_1.regex_match(input_string)
    assert result_match == ["Hi", "42"]

    # Replace mode - new instance due to single-run-per-instance rule
    regex_block_replace = RegexMatch()
    regex_block_replace.regex = r"\w+"
    regex_block_replace.replace_with = "X"
    result_replace = await regex_block_replace.regex_match(input_string)
    assert result_replace == "X X"

    # Back to match mode - new instance
    regex_block_match_2 = RegexMatch()
    regex_block_match_2.regex = r"\w+"
    result_match_again = await regex_block_match_2.regex_match(input_string)
    assert result_match_again == ["Hi", "42"]
