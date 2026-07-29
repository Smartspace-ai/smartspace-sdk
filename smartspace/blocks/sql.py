import datetime
from decimal import Decimal
from typing import Annotated, Any, Dict, List, Union


from smartspace.core import Block, Config, Metadata, metadata, step
from smartspace.enums import BlockCategory, InputLanguage

@metadata(
    category=BlockCategory.WEB,
    description=(
        "Executes an async SQL query via SQLAlchemy against any supported database. "
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
class SQL(Block):
    connection_string: Annotated[str, Config()]
    query: Annotated[
        str,
        Config(),
        Metadata(
            language=InputLanguage.SQL,
            description=(
                "SQL statement, e.g. "
                "SELECT * FROM orders WHERE status = :status.\n"
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
            Boolean, Date, DateTime, Float, Integer,
            LargeBinary, Numeric, String, Time,
            bindparam, text

        )
        from sqlalchemy.ext.asyncio import create_async_engine
        from sqlalchemy.sql.elements import BindParameter
        from sqlalchemy.types import TypeEngine

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
            Decimal: Numeric(),   # <--- Decimal support added here
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
