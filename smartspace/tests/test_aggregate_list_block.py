import pytest

from smartspace.blocks.lists import AggregateList


@pytest.mark.asyncio
async def test_aggregate_list_empty():
    block = AggregateList()
    result = await block.aggregate()
    assert result == []


@pytest.mark.asyncio
async def test_aggregate_list_single_item():
    block = AggregateList()
    result = await block.aggregate(1)
    assert result == [1]


@pytest.mark.asyncio
async def test_aggregate_list_multiple_items():
    block = AggregateList()
    result = await block.aggregate(1, 2, 3)
    assert result == [1, 2, 3]


@pytest.mark.asyncio
async def test_aggregate_list_with_lists():
    block = AggregateList()
    result = await block.aggregate([1, 2], [3, 4])
    assert result == [1, 2, 3, 4]


@pytest.mark.asyncio
async def test_aggregate_mixed_types():
    block = AggregateList()
    result = await block.aggregate([1, 2], 3, [4, 5])
    assert result == [1, 2, 3, 4, 5]


@pytest.mark.asyncio
async def test_aggregate_strings():
    block = AggregateList()
    result = await block.aggregate("a", "b", "c")
    assert result == ["a", "b", "c"]


@pytest.mark.asyncio
async def test_aggregate_list_of_strings():
    block = AggregateList()
    result = await block.aggregate(["a", "b"], "c", ["d"])
    assert result == ["a", "b", "c", "d"]


@pytest.mark.asyncio
async def test_aggregate_list_of_lists():
    block = AggregateList()
    result = await block.aggregate([1, {"a": 1}], [3, 4])
    assert result == [1, {"a": 1}, 3, 4]
