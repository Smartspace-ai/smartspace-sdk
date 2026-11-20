import pytest

from smartspace.blocks.sql_1_1_0 import SQL_1_1_0, count_statements
from smartspace.core import BlockError

CONNECTION_STRINGS = {
    "mssql": "mssql+aioodbc://u:p@localhost:1433/db?driver=ODBC+Driver+17+for+SQL+Server",
    "mysql": "mysql+aiomysql://u:p@localhost:3306/db",
    "postgresql": "postgresql+asyncpg://u:p@localhost:5432/db",
    "oracle": "oracle+aioodbc://u:p@localhost:1521/svc",
}


@pytest.mark.parametrize(
    "backend, query, expected",
    [
        ("mssql", "SELECT 1", 1),
        ("mssql", "SELECT 1;", 1),
        ("mssql", "SELECT 1;;", 1),
        ("mssql", "  SELECT 1 ;  -- done", 1),
        ("mssql", "SELECT 1; SELECT 2", 2),
        ("mssql", "SELECT 1; SELECT 2; SELECT 3;", 3),
        ("mssql", "SELECT * FROM vegetables; SELECT * FROM fruits;", 2),
        ("mssql", "SELECT 'a;b' AS s", 1),
        ("mssql", "SELECT 1 /* a; b */", 1),
        ("mssql", "SELECT 1 -- a; b\n; SELECT 2", 2),
        ("mssql", "-- only a comment", 0),
        ("mssql", "", 0),
        (
            "mssql",
            "SELECT name, CASE WHEN id = 1 THEN 'first' ELSE 'other' END AS label "
            "FROM vegetables",
            1,
        ),
        ("mysql", "SELECT 'it\\'s;ok' AS s", 1),
        ("mysql", "CREATE TABLE t (id INT); INSERT INTO t VALUES (1);", 2),
        ("postgresql", "SELECT $$x;y$$ AS q", 1),
        ("postgresql", "SELECT 1; SELECT 2", 2),
        ("oracle", "SELECT 1 FROM dual; SELECT 2 FROM dual", 2),
        # A backend that has no sqlglot mapping falls back to the generic dialect.
        ("sqlite", "SELECT 1; SELECT 2", 2),
        ("sqlite", "SELECT 'a;b'", 1),
    ],
)
def test_count_statements(backend, query, expected):
    assert count_statements(query, backend) == expected


@pytest.mark.parametrize("backend", ["mssql", "MSSQL", "Mssql"])
def test_count_statements_ignores_backend_name_case(backend):
    # `[a;b]` is a bracketed identifier in T-SQL only, so the generic dialect would split it.
    assert count_statements("SELECT [a;b] FROM t", backend) == 1


@pytest.mark.xfail(
    strict=True,
    reason=(
        "Known limitation: T-SQL accepts statements with no semicolon between them, "
        "and the check only counts semicolons."
    ),
)
def test_count_statements_misses_t_sql_statements_without_semicolons():
    assert count_statements("SELECT 1 AS a SELECT 2 AS b", "mssql") == 2


def test_count_statements_reports_unparseable_query():
    with pytest.raises(BlockError, match="Could not parse"):
        count_statements("SELECT 'unterminated", "mssql")


def test_block_name_and_version():
    assert SQL_1_1_0.name == "SQL"
    assert SQL_1_1_0.version == "1.1.0"


def _block(backend: str, query: str) -> SQL_1_1_0:
    block = SQL_1_1_0()
    block.connection_string = CONNECTION_STRINGS[backend]
    block.query = query
    return block


@pytest.mark.asyncio
@pytest.mark.parametrize("backend", list(CONNECTION_STRINGS))
async def test_run_rejects_multiple_statements_before_connecting(backend, mocker):
    create_engine = mocker.patch("sqlalchemy.ext.asyncio.create_async_engine")
    block = _block(backend, "SELECT 1; SELECT 2")

    with pytest.raises(BlockError, match="Only one SQL statement is allowed") as exc:
        await block.run()

    assert "2 were found" in exc.value.message
    create_engine.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "query", ["", "   ", ";", " ; ; ", "-- nothing here", "/* nothing */;"]
)
async def test_run_rejects_an_empty_query_before_connecting(query, mocker):
    create_engine = mocker.patch("sqlalchemy.ext.asyncio.create_async_engine")
    block = _block("mssql", query)

    with pytest.raises(BlockError, match="query is empty"):
        await block.run()

    create_engine.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "query", ["SELECT 1", "SELECT 1;", "SELECT 'a;b' AS s;", "SELECT :a AS x"]
)
async def test_run_allows_a_single_statement(query, mocker):
    class _Reached(Exception):
        pass

    create_engine = mocker.patch(
        "sqlalchemy.ext.asyncio.create_async_engine", side_effect=_Reached
    )
    block = _block("mssql", query)

    with pytest.raises(_Reached):
        await block.run(a=1)

    create_engine.assert_called_once()
