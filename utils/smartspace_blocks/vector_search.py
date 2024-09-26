from typing import Annotated

from injector import ClassAssistedBuilder, inject
from smartspace.core import (
    Config,
    WorkSpaceBlock,
    metadata,
    step,
)
from smartspace.enums import BlockCategory

from app.integrations.embeddings.core import EmbeddingsService
from app.integrations.search.core import SearchService
from app.integrations.search.models import SearchResult
from app.integrations.ss_config_api.core import SSConfigAPIClient
from app.integrations.tokenization.core import TokenizationService
from app.utils.search import get_vector_search


@metadata(category=BlockCategory.DATA)
class VectorSearch(WorkSpaceBlock):
    topn: Annotated[int, Config()] = 10
    token_limit: Annotated[int, Config()] = 2000
    dataspace_ids: Annotated[list[str] | None, Config()] = []

    @inject
    def __init__(
        self,
        search_service: SearchService,
        config_client: SSConfigAPIClient,
        embeddings_service_builder: ClassAssistedBuilder[EmbeddingsService],
        tokenization_service_builder: ClassAssistedBuilder[TokenizationService],
    ):
        super().__init__()

        self.search_service = search_service
        self.config_client = config_client
        self.embeddings_service_builder = embeddings_service_builder
        self.tokenization_service_builder = tokenization_service_builder

    @step(output_name="results")
    async def search(
        self,
        queries: list[str],
    ) -> list[SearchResult]:
        if self.workspace is None:
            raise Exception("VectorSearch can only be used in a workspace")

        embeddings_config = await self.config_client.get_embeddings_config()

        embeddings_service: EmbeddingsService = self.embeddings_service_builder.build(
            config=embeddings_config
        )

        tokenization_service: TokenizationService = (
            self.tokenization_service_builder.build(config=embeddings_config)
        )

        embeddings = await embeddings_service.get_embeddings(input=queries)

        search_results: list[SearchResult] = []

        query_token_limit = int(self.token_limit / len(queries))
        for query_embedding in embeddings:
            search_results.extend(
                await get_vector_search(
                    search_service=self.search_service,
                    query_embeddings=query_embedding,
                    dataspace_ids=(
                        self.workspace.dataspace_ids
                        if self.dataspace_ids is None or len(self.dataspace_ids) == 0
                        else self.dataspace_ids
                    )
                    or [],
                    tokenization_service=tokenization_service,
                    embeddings_service=embeddings_service,
                    token_limit=query_token_limit,
                    topn=self.topn * 5,
                )
            )

        search_results.sort(key=lambda x: x.score, reverse=True)

        unique_results: list[SearchResult] = []
        total_tokens_from_unique_results = 0
        for r in search_results:
            if not any(r.id == u.id for u in unique_results):
                # TODO this over estimates the token count, but at least it isn't under
                token_count = len(
                    tokenization_service.encode_tokens(
                        text=f'[{{"content": "{r.content}", "name": "source_999"}}]'
                    )
                )
                if token_count + total_tokens_from_unique_results > self.token_limit:
                    continue

                unique_results.append(r)
                total_tokens_from_unique_results += token_count

        search_results_dict: dict[str, SearchResult] = {}
        final_search_results: list[SearchResult] = []

        for result in unique_results:
            if not result.path:
                final_search_results.append(result)
            else:
                if result.path not in search_results_dict:
                    search_results_dict[result.path] = result
                else:
                    existing = search_results_dict[result.path]
                    search_results_dict[result.path].score = max(
                        existing.score, result.score
                    )
                    search_results_dict[
                        result.path
                    ].content = f"{existing.content}\n{result.content}"

        final_search_results = final_search_results + list(search_results_dict.values())
        final_search_results.sort(key=lambda x: x.score, reverse=True)
        final_search_results = final_search_results[: self.topn]

        return final_search_results
