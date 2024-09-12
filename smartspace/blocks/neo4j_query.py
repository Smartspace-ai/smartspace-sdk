import json
from typing import Any

from neo4j import GraphDatabase

from smartspace.core import (
    Block,
    Config,
    metadata,
    step,
)
from smartspace.enums import BlockCategory


@metadata(
    category=BlockCategory.DATA,
    description="Performs a query on a Neo4j Server",
)
class Neo4jQuery(Block):
    connection_url: Config[str] = (
        "neo4j+s://24e8f33c.databases.neo4j.io"  # neo4j+s://xxxxxxxx.databases.neo4j.io". If not using default port, add port number at the end, e.g. "neo4j+s://xxxxxxxx.databases.neo4j.io:7687"
    )
    user: Config[str] = "neo4j"
    password: Config[str] = "3HJ4A5Bw9mgcBV5Yzn8VWzXDWRT5gJIExfIWucxp48s"
    query: Config[str] = "MATCH (n) RETURN n LIMIT 5"
    database: Config[str] = "neo4j"  # "neo4j" # Database name
    params: Config[dict] = {}  # Parameters to pass to the query

    @step(output_name="results")
    async def search(
        self,
        run: Any,
    ) -> list[Any]:
        driver = GraphDatabase.driver(
            self.connection_url,
            auth=(self.user, self.password),
        )
        try:
            with driver.session(database=self.database) as session:
                if self.params:
                    result = session.run(self.query, self.params)
                else:
                    result = session.run(self.query)

                results = []
                if result.keys():
                    results = [record.data() for record in result]

                driver.close()
                # convert json to string
                results_str = json.dumps(results)
                results_dict = [{"image": None, "text": results_str}]
                return results_dict
        except Exception as e:
            driver.close()
            print(f"Neo4j Aura Error: {e}")
            results_dict = [{"image": None, "text": "No results found"}]
            return results_dict
