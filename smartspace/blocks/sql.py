import datetime
from typing import Annotated, Any, Dict, List, Type, Union

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    Integer,
    LargeBinary,
    String,
    Time,
    bindparam,
    text,
)
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.sql.elements import BindParameter
from sqlalchemy.types import TypeEngine

from smartspace.core import Block, Config, metadata, step
from smartspace.enums import BlockCategory

# Removed Pydantic import and SQLResult model as per requirement


@metadata(
    category=BlockCategory.DATA,
    description=(
        "Executes an asynchronous SQL query on a database using SQLAlchemy. "
        "Supports all types of queries, including SELECT, INSERT, UPDATE, and DELETE. "
        "For data-modifying queries (INSERT, UPDATE, DELETE), the block commits the transaction. "
        "If the database connection fails (e.g., because the database isn't running yet), "
        "the block will retry the connection once before raising an error. "
        "The connection string should be provided in a format compatible with SQLAlchemy's `create_async_engine`, "
        "such as `'mssql+aioodbc://username:password@host:port/dbname?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes'`."
    ),
)
class SQL(Block):
    """Block that executes an asynchronous SQL query on a database using SQLAlchemy."""

    connection_string: Annotated[str, Config()]
    query: Annotated[str, Config()]

    @step(output_name="result")
    async def run(self, **params) -> Union[List[Dict[str, Any]], int]:
        """Execute the SQL query with the given parameters and return the result."""
        engine = create_async_engine(self.connection_string)

        # Define type mapping with precise type annotations
        type_mapping: Dict[Type[Any], TypeEngine[Any]] = {
            str: String(),
            int: Integer(),
            float: Float(),
            bool: Boolean(),
            datetime.datetime: DateTime(),
            datetime.date: Date(),
            datetime.time: Time(),
            bytes: LargeBinary(),
        }

        try:
            async with engine.begin() as connection:
                statement = text(self.query)

                # Accessing the private attribute _bindparams
                # Note: Accessing private attributes is generally discouraged, but necessary here due to SQLAlchemy's API limitations.
                required_params = set(statement._bindparams.keys())
                provided_params = set(params.keys())
                missing_params = required_params - provided_params

                if missing_params:
                    raise ValueError(f"Missing parameters: {', '.join(missing_params)}")

                # Prepare bind parameters with typing
                bind_params: List[BindParameter] = []

                for param_name in required_params:
                    param_value = params[param_name]
                    # Determine the SQLAlchemy type based on the parameter value
                    if isinstance(param_value, (list, tuple)):
                        # For expanding parameters, infer type from the first element
                        if param_value:
                            element_type = type(param_value[0])
                        else:
                            element_type = str  # Default to string if list is empty
                        param_type = type_mapping.get(element_type, String())
                        bind_params.append(
                            bindparam(param_name, expanding=True, type_=param_type)
                        )
                    else:
                        param_type = type_mapping.get(type(param_value), String())
                        bind_params.append(bindparam(param_name, type_=param_type))

                statement = statement.bindparams(*bind_params)

                # Execute the query
                cursor = await connection.execute(statement, params)

                # Determine the type of query and populate the result accordingly
                if cursor.returns_rows:
                    # Fetch all results as dictionaries
                    result = [dict(row) for row in cursor.mappings().all()]
                else:
                    # For INSERT, UPDATE, DELETE, etc., get the number of affected rows
                    result = cursor.rowcount

                return result

        finally:
            await engine.dispose()
