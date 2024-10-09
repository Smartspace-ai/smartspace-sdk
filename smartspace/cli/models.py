from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from smartspace.models import BlockInterface


class PublishedBlockSet(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    name: str
    block_interfaces: Annotated[
        dict[str, dict[str, BlockInterface]], Field(alias="blockInterfaces")
    ]
    source_code_uri: Annotated[str | None, Field(alias="sourceCodeUri")] = None
    connection_id: Annotated[str | None, Field(alias="connectionId")] = None
    created_by_user_id: Annotated[str | None, Field(alias="createdByUserId")] = None
