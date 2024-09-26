from typing import Annotated, Any

from injector import inject
from smartspace.core import (
    Block,
    Config,
    metadata,
    step,
)
from smartspace.enums import BlockCategory

from app.blocks.models import GetAllDocumentsResult
from app.integrations.search.core import SearchService


@metadata(category=BlockCategory.DATA)
class GetAllDocuments(Block):
    dataspace_id: Annotated[str, Config()]

    @inject
    def __init__(
        self,
        search_service: SearchService,
    ):
        super().__init__()

        self.search_service = search_service

    @step(output_name="documents")
    async def get_documents(
        self,
        run: Any,
    ) -> list[GetAllDocumentsResult]:
        results = await self.search_service.get_all_documents(
            dataspace_id=self.dataspace_id
        )
        return [GetAllDocumentsResult(path=r.path, content=r.content) for r in results]
