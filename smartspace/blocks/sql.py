# from typing import Annotated, Any

# import pymssql  # type: ignore

# from smartspace.core import (
#     Block,
#     Config,
#     metadata,
#     step,
# )
# from smartspace.enums import BlockCategory


# @metadata(
#     category=BlockCategory.DATA,
#     description="Performs a query on a MS SQL Server",
# )
# class SQLServer(Block):
#     server: Annotated[str, Config()]
#     user: Annotated[str, Config()]
#     password: Annotated[str, Config()]
#     database: Annotated[str, Config()]
#     port: Annotated[str, Config()]
#     query: Annotated[str, Config()]

#     @step(output_name="results")
#     async def search(
#         self,
#         params: list[Any] | dict[str, Any],
#     ) -> Any:
#         conn = pymssql.connect(
#             server=self.server,
#             user=self.user,
#             password=self.password,
#             database=self.database,
#             port=self.port,
#         )
#         cursor = conn.cursor()

#         if isinstance(params, list):
#             query = self.query.format(
#                 params=", ".join([f"'{str(param)}'" for param in params])
#             )
#         else:
#             params_dict = {
#                 key: value
#                 if not isinstance(value, list)
#                 else ", ".join([f"'{str(v)}'" for v in value])
#                 for key, value in params.items()
#             }
#             query = self.query.format(**params_dict)

#         cursor.execute(query)

#         results = []
#         if cursor.description:
#             columns = [column[0] for column in cursor.description]
#             results = [dict(zip(columns, row)) for row in cursor.fetchall()]  # type: ignore

#         if any(
#             keyword in self.query.strip().upper()
#             for keyword in ("INSERT", "UPDATE", "DELETE")
#         ):
#             conn.commit()

#         cursor.close()
#         conn.close()

#         return results
