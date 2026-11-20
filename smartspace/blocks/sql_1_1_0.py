import datetime
from decimal import Decimal
from typing import Annotated, Any, Dict, List, Union

from smartspace.core import Block, BlockError, Config, Metadata, metadata, step
from smartspace.enums import BlockCategory, InputLanguage

# SQLAlchemy backend name -> sqlglot dialect name. A backend that is not listed
# here is tokenized with sqlglot's generic dialect.
_SQLGLOT_DIALECTS = {
    "mssql": "tsql",
    "mysql": "mysql",
    "postgresql": "postgres",
    "oracle": "oracle",
}


def count_statements(query: str, backend: str) -> int:
    """Count the non-empty statements in `query`.

    Statements are separated by semicolons that sit outside string literals,
    comments and dollar-quoted bodies. A trailing semicolon, repeated
    semicolons and comment-only text do not add to the count.
    """
    from sqlglot.dialects.dialect import Dialect
    from sqlglot.errors import TokenError
    from sqlglot.tokens import TokenType

    dialect = Dialect.get_or_raise(_SQLGLOT_DIALECTS.get(backend.lower(), ""))
    try:
        tokens = dialect.tokenize(query)
    except TokenError as e:
        raise BlockError(f"Could not parse the SQL query: {e}")

    count = 0
    statement_has_tokens = False
    for token in tokens:
        if token.token_type == TokenType.SEMICOLON:
            count += statement_has_tokens
            statement_has_tokens = False
        else:
            statement_has_tokens = True

    return count + statement_has_tokens


@metadata(
    category=BlockCategory.WEB,
    description=(
        "Executes a single async SQL statement via SQLAlchemy against any supported database. "
        "A query that contains more than one statement is rejected with an error. "
        "Ensure your `connection_string` uses the correct dialect+driver prefix and proper URL encoding. Examples:\n"
        "  • MySQL: mysql+aiomysql://<user>:<password>@<host>:<port>/<dbname>?charset=utf8mb4\n"
        "  • SQL Server (ODBC): mssql+aioodbc://<user>:<password>@<host>:<port>/<dbname>?driver=ODBC+Driver+17+for+SQL+Server\n"
        "  • Oracle (ODBC): oracle+aioodbc://<user>:<password>@<host>:<port>/<servicename>\n"
        "  • PostgreSQL: postgresql+asyncpg://<user>:<password>@<host>:<port>/<dbname>\n"
        "Percent-encode special characters in credentials (e.g., `^` → `%5E`)."
    ),
    icon="fa-database",
    label="sql query, database, sqlalchemy, select, async db, relational",
)
class SQL_1_1_0(Block):
    connection_string: Annotated[str, Config()]
    query: Annotated[
        str,
        Config(),
        Metadata(
            language=InputLanguage.SQL,
            description=(
                "A single SQL statement, e.g. "
                "SELECT * FROM orders WHERE status = :status.\n"
                "\n"
                "A query that contains more than one statement (separated by "
                "semicolons) is rejected, so use one block per statement.\n"
                "\n"
                ":name placeholders are bind parameters — each one is filled "
                "from the block's input pin of the same name, safely "
                "parameterised (never string-interpolated).\n"
                "\n"
                "Runs against the connection_string database, so use that "
                "engine's dialect. SELECTs return a list of row objects; "
                "other statements return the affected row count."
            ),
        ),
    ]

    @step(output_name="result")
    async def run(self, **params) -> Union[List[Dict[str, Any]], int]:
        from sqlalchemy import (
            Boolean,
            Date,
            DateTime,
            Float,
            Integer,
            LargeBinary,
            Numeric,
            String,
            Time,
            bindparam,
            text,
        )
        from sqlalchemy.engine import make_url
        from sqlalchemy.ext.asyncio import create_async_engine
        from sqlalchemy.sql.elements import BindParameter
        from sqlalchemy.types import TypeEngine

        # Reject empty and multi-statement queries before connecting to the database.
        backend = make_url(self.connection_string).get_backend_name()
        statement_count = count_statements(self.query, backend)
        if statement_count == 0:
            raise BlockError(
                "The SQL query is empty. Provide exactly one SQL statement to run."
            )
        if statement_count > 1:
            raise BlockError(
                f"Only one SQL statement is allowed per query, but {statement_count} "
                "were found. Use a separate SQL block for each statement."
            )

        # create the async engine (driver auto-picked from connection_string)
        engine = create_async_engine(self.connection_string, future=True)

        # Python type → SQLAlchemy type map
        type_mapping: Dict[type, TypeEngine] = {
            str: String(),
            int: Integer(),
            float: Float(),
            bool: Boolean(),
            datetime.datetime: DateTime(),
            datetime.date: Date(),
            datetime.time: Time(),
            bytes: LargeBinary(),
            Decimal: Numeric(),
        }

        try:
            async with engine.begin() as conn:
                stmt = text(self.query)

                # Determine required bind params
                required = set(stmt._bindparams.keys())
                missing = required - set(params)
                if missing:
                    raise ValueError(f"Missing params: {', '.join(missing)}")

                # Build bindparam objects with correct types
                binds: List[BindParameter] = []
                for name in required:
                    val = params[name]
                    if isinstance(val, (list, tuple)):
                        elem_t = type(val[0]) if val else str
                        sql_t = type_mapping.get(elem_t, String())
                        binds.append(bindparam(name, expanding=True, type_=sql_t))
                    else:
                        sql_t = type_mapping.get(type(val), String())
                        binds.append(bindparam(name, type_=sql_t))

                stmt = stmt.bindparams(*binds)

                # Execute and fetch
                result = await conn.execute(stmt, params)
                if result.returns_rows:
                    return [dict(r) for r in result.mappings().all()]
                else:
                    return result.rowcount
        finally:
            await engine.dispose()
