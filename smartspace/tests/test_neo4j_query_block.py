from unittest.mock import Mock

import pytest
from neo4j.exceptions import ConfigurationError

from smartspace.blocks.neo4j_query import Neo4jQuery  # Adjust import path as needed


@pytest.fixture(scope="function")
def mock_neo4j_block():
    return Mock(
        spec=Neo4jQuery,
        connection_url="neo4j+s://24e8f33c.databases.neo4j.io",
        user="neo4j",
        password="3HJ4A5Bw9mgcBV5Yzn8VWzXDWRT5gJIExfIWucxp48s",
        query="MATCH (n) RETURN n LIMIT 5",
        database="neo4j",
        paras={},
    )


@pytest.mark.asyncio
async def test_neo4j_query_success(mock_neo4j_block: Mock):
    neo4j_query = Neo4jQuery(Mock(), Mock())
    results = await neo4j_query.search._fn(mock_neo4j_block, run=Mock())
    assert len(results) == 1


# test invalid connection URL
@pytest.mark.asyncio
async def test_neo4j_query_invalid_connection_url(mock_neo4j_block: Mock):
    mock_neo4j_block.connection_url = "invalid_url"
    neo4j_query = Neo4jQuery(Mock(), Mock())
    with pytest.raises(ConfigurationError):
        await neo4j_query.search._fn(mock_neo4j_block, run=Mock())


# test invalid user
@pytest.mark.asyncio
async def test_neo4j_query_invalid_user_or_password(mock_neo4j_block: Mock):
    mock_neo4j_block.user = "invalid"

    neo4j_query = Neo4jQuery(Mock(), Mock())
    result = await neo4j_query.search._fn(mock_neo4j_block, run=Mock())
    assert result == [{"image": None, "text": "No results found"}]


# test invalid password
@pytest.mark.asyncio
async def test_neo4j_query_invalid_password(mock_neo4j_block: Mock):
    mock_neo4j_block.password = "invalid"
    neo4j_query = Neo4jQuery(Mock(), Mock())
    results = await neo4j_query.search._fn(mock_neo4j_block, run=Mock())
    assert results == [{"image": None, "text": "No results found"}]


# test invalid query
@pytest.mark.asyncio
async def test_neo4j_query_invalid_query(mock_neo4j_block: Mock):
    mock_neo4j_block.query = "invalid query"
    neo4j_query = Neo4jQuery(Mock(), Mock())
    results = await neo4j_query.search._fn(mock_neo4j_block, run=Mock())
    assert results == [{"image": None, "text": "No results found"}]


# test invalid database
@pytest.mark.asyncio
async def test_neo4j_query_invalid_database(mock_neo4j_block: Mock):
    mock_neo4j_block.database = "invalid database"
    neo4j_query = Neo4jQuery(Mock(), Mock())
    results = await neo4j_query.search._fn(mock_neo4j_block, run=Mock())
    assert results == [{"image": None, "text": "No results found"}]


# test invalid database
@pytest.mark.asyncio
async def test_neo4j_query_paras(mock_neo4j_block: Mock):
    mock_neo4j_block.query = "MATCH (n) RETURN n LIMIT $limit_num"
    mock_neo4j_block.paras = {"limit_num": 3}
    neo4j_query = Neo4jQuery(Mock(), Mock())
    results = await neo4j_query.search._fn(mock_neo4j_block, run=Mock())
    assert len(results) == 1


# @pytest.mark.asyncio
# async def test_neo4j_query_success(mock_neo4j_block: Mock):
#     # Mock the GraphDatabase.driver
#     mock_driver = MagicMock()
#     mock_session = MagicMock()
#     mock_result = MagicMock()

#     # Set up the mock result
#     mock_result.keys.return_value = ["name", "age"]
#     mock_result.__iter__.return_value = [
#         {"name": "Alice", "age": 30},
#         {"name": "Bob", "age": 25},
#     ]

#     # Set up the mock session
#     mock_session.__enter__.return_value.run.return_value = mock_result

#     # Set up the mock driver
#     mock_driver.session.return_value = mock_session

#     with patch.object(
#         GraphDatabase, "driver", return_value=mock_driver
#     ) as mock_driver_class:
#         neo4j_query = Neo4jQuery(Mock(), Mock())
#         results = await neo4j_query.search._fn(mock_neo4j_block)

#     assert len(results) == 2
#     assert results[0]["name"] == "Alice"
#     assert results[1]["age"] == 25

#     # Verify that the driver was created with correct parameters
#     mock_driver_class.assert_called_once_with(
#         mock_neo4j_block.connection_url,
#         auth=(mock_neo4j_block.user, mock_neo4j_block.password),
#     )
#     # Verify that the session was created with the correct database
#     mock_driver.session.assert_called_once_with(database="neo4j")
#     # Verify that the driver was closed
#     mock_driver.close.assert_called_once()


# @pytest.mark.asyncio
# async def test_neo4j_query_empty_result(mock_neo4j_block: Mock):
#     mock_driver = MagicMock()
#     mock_session = MagicMock()
#     mock_result = MagicMock()

#     # Set up an empty result
#     mock_result.keys.return_value = []
#     mock_result.__iter__.return_value = []

#     mock_session.__enter__.return_value.run.return_value = mock_result
#     mock_driver.session.return_value = mock_session

#     with patch.object(
#         GraphDatabase, "driver", return_value=mock_driver
#     ) as mock_driver_class:
#         neo4j_query = Neo4jQuery(Mock(), Mock())
#         results = await neo4j_query.search._fn(mock_neo4j_block)

#     assert len(results) == 0
#     mock_driver_class.assert_called_once_with(
#         mock_neo4j_block.connection_url,
#         auth=(mock_neo4j_block.user, mock_neo4j_block.password),
#     )
#     mock_driver.session.assert_called_once_with(database="neo4j")
#     mock_driver.close.assert_called_once()


# @pytest.mark.asyncio
# async def test_neo4j_query_exception(mock_neo4j_block: Mock):
#     mock_driver = Mock()
#     mock_driver.session.side_effect = Exception("Connection error")

#     with patch.object(GraphDatabase, "driver", return_value=mock_driver):
#         neo4j_query = Neo4jQuery(Mock(), Mock())
#         results = await neo4j_query.search._fn(mock_neo4j_block)

#     assert results == []
#     mock_driver.close.assert_called_once()
