from typing import Annotated, Any

from injector import inject
from numpy import dot
from numpy.linalg import norm
from pydantic import BaseModel, ConfigDict, Field
from smartspace.core import Block, Config, Output, State, Tool, callback, metadata, step
from smartspace.enums import BlockCategory
from smartspace.models import File

from app.blocks.native.data_blocks.files import get_file_content
from app.blocks.native.files_blocks.models import Chunk
from app.integrations.blob_storage.core import BlobService
from app.integrations.embeddings.core import DefaultEmbeddingsService
from app.utils.pandoc import (
    PandocToFormats,
    convert_document,
    get_file_extension,
    is_valid_format,
)


class ChunkData(BaseModel):
    chunk: Chunk
    embedding: list[float]


class ChunkedFile(BaseModel):
    content: str
    filename: str
    chunks: list[ChunkData]


class ChunkToCompare(BaseModel):
    filename: str
    chunk: ChunkData


class FileInfo(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    filename: str
    content_length: Annotated[int, Field(alias="contentLength")]


@metadata(
    category=BlockCategory.FUNCTION,
    description="""
    Store and search embeddings in an in-memory vector database.

    Args:
        top_k: The number of results to return in search.

    Steps:
        1: Update index with embeddings.
        2: Search index to return relevant documents.

    """,
)
class FileStore(Block):
    top_k: Annotated[int, Config()] = 5
    data: Annotated[Any, State()] = None
    files_state: Annotated[list[ChunkedFile], State()] = []
    pending_file_count: Annotated[int, State()] = 0
    all_files_state: Annotated[list[FileInfo], State()] = []
    new_files_state: Annotated[list[FileInfo], State()] = []

    class ChunkTool(Tool):
        def run(self, file_content: str) -> list[Chunk]: ...

    chunk: ChunkTool

    all_files: Output[list[FileInfo]]
    files: Output[list[FileInfo]]

    @inject
    def __init__(
        self, embeddings_service: DefaultEmbeddingsService, blob_service: BlobService
    ):
        super().__init__()
        self.embeddings_service = embeddings_service
        self.blob_service = blob_service

    async def get_file_content(self, file: File) -> str:
        file_extension = get_file_extension(file.name or "")
        if not is_valid_format(file_extension):
            # get raw content
            file_content = await get_file_content(file, self.blob_service)
        else:
            # convert to markdown
            file_data = await self.blob_service.get_blob(file.uri)
            file_content = await convert_document(
                file_name=file.name or "",
                file_bytes=file_data.bytes.read(),
                to_format=PandocToFormats.MARKDOWN,
            )
        return file_content

    @step()
    async def add_files(self, files: list[File]):
        file_infos: list[FileInfo] = []
        self.pending_file_count = len(files)

        if len(files) == 0:
            self.all_files.send(self.all_files_state)
            self.files.send([])

        else:
            for f in files:
                file_content = await self.get_file_content(f)
                file_info = FileInfo(
                    filename=f.name or "",
                    content_length=len(file_content),
                )
                file_infos.append(file_info)
                await self.chunk.call(file_content).then(
                    lambda chunks: self.handle_chunks(
                        file_info.filename, file_content, chunks
                    )
                )

            self.all_files_state.extend(file_infos)
            self.new_files_state = file_infos

    @callback()
    async def handle_chunks(self, filename: str, content: str, chunks: list[Chunk]):
        self.files_state.append(
            ChunkedFile(
                content=content,
                filename=filename,
                chunks=[
                    ChunkData(
                        chunk=chunk,
                        embedding=(
                            await self.embeddings_service.get_embeddings(chunk.content)
                        )[0],
                    )
                    for chunk in chunks
                ],
            )
        )
        self.pending_file_count -= 1

        if self.pending_file_count == 0:
            self.all_files.send(self.all_files_state)
            self.files.send(self.new_files_state)

    @step(output_name="file_content")
    async def get(
        self,
        filename: str,
    ) -> str:
        for f in self.files_state:
            if f.filename == filename:
                return f.content

        return f"No file found with name {filename}"

    @step(output_name="chunks")
    async def semantic_search(
        self,
        query: str,
    ) -> list[str]:
        query_embedding = await self.embeddings_service.get_embeddings(query)
        query_vector = query_embedding[0]

        chunks_to_compare = [
            ChunkToCompare(filename=file.filename, chunk=chunk)
            for file in self.files_state
            for chunk in file.chunks
        ]

        similarities = [
            (
                dot(query_vector, c.chunk.embedding)
                / (norm(query_vector) * norm(c.chunk.embedding)),
                c,
            )
            for c in chunks_to_compare
        ]

        sorted_chunks = [
            c[1] for c in sorted(similarities, key=lambda c: c[0], reverse=True)
        ]
        top_chunks = sorted_chunks[: self.top_k]

        return [c.chunk.chunk.content for c in top_chunks]
