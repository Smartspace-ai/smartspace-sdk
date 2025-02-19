import pytest

from smartspace.blocks.lists import Slice


@pytest.mark.asyncio
async def test_slice_list_default():
    block = Slice()
    result = await block.slice([1, 2, 3, 4, 5])
    assert result == []  # Default start=0, end=0 returns empty


@pytest.mark.asyncio
async def test_slice_list_with_end():
    block = Slice()
    block.end = 3
    result = await block.slice([1, 2, 3, 4, 5])
    assert result == [1, 2, 3]


@pytest.mark.asyncio
async def test_slice_list_with_start():
    block = Slice()
    block.start = 2
    block.end = 5
    result = await block.slice([1, 2, 3, 4, 5])
    assert result == [3, 4, 5]


@pytest.mark.asyncio
async def test_slice_string():
    block = Slice()
    block.start = 1
    block.end = 4
    result = await block.slice("Hello World")
    assert result == "ell"


@pytest.mark.asyncio
async def test_slice_empty_list():
    block = Slice()
    block.end = 3
    result = await block.slice([])
    assert result == []


@pytest.mark.asyncio
async def test_slice_empty_string():
    block = Slice()
    block.end = 3
    result = await block.slice("")
    assert result == ""


@pytest.mark.asyncio
async def test_slice_negative_indices():
    block = Slice()
    block.start = -3
    block.end = -1
    result = await block.slice([1, 2, 3, 4, 5])
    assert result == [3, 4]


@pytest.mark.asyncio
async def test_slice_with_list_input():
    block = Slice()
    block.start = 1
    block.end = 1
    result = await block.slice([1, 2, 3, 4, 5])
    assert result == 2


@pytest.mark.asyncio
async def test_slice_with_string_input():
    block = Slice()
    block.start = 1
    block.end = 1
    result = await block.slice("Hello World")
    assert result == "e"
