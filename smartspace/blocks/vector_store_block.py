from typing import List

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from smartspace.core import Block, Config, metadata, step
from smartspace.enums import BlockCategory
from smartspace.models import InMemorySearchResult


@metadata(
    category=BlockCategory.FUNCTION,
    description="""
    Store and search embeddings in an in-memory vector database.

    Args:
        embedding_size: The size of the embedding vectors.
        top_k: The number of results to return in search.

    Steps:
        1: Update index with embeddings.
        2: Search index to return relevant documents.

    """,
)
class VectorStore(Block):
    top_k: Config[int] = 5
    client = QdrantClient(":memory:")

    files: list = []
    embedding_size = 0

    @step()
    async def create_store(
        self,
        filecontent: str,
        filename: str,
        chunk_positions: list[tuple[int, int]],
        chunk_embeddings: list[list[float]],
    ):
        # store the file content
        chunk_names = [f"{filename}_chunk_{i}" for i in range(len(chunk_positions))]
        file_obj = {
            "filecontent": filecontent,
            "filename": filename,
            "chunk_names": chunk_names,
            "chunk_positions": chunk_positions,
        }

        self.files.append(file_obj)

        # store the embeddings in the in-memory vector database
        # get embeeding size
        if self.embedding_size == 0:
            self.embedding_size = len(chunk_embeddings[0])
            self.client.recreate_collection(
                collection_name="documents",
                vectors_config=VectorParams(
                    size=self.embedding_size,
                    distance=Distance.COSINE,
                ),
            )

        else:  # check if the embedding size is consistent
            if len(chunk_embeddings[0]) != self.embedding_size:
                raise ValueError("The embedding size should be consistent")

        points = [
            PointStruct(
                id=i,
                vector=embedding,
                payload={
                    "filename": filename,
                    "chunk_name": chunk_name,
                    "chunk_position": position,
                },
            )
            for i, (embedding, chunk_name, position) in enumerate(
                zip(chunk_embeddings, chunk_names, chunk_positions)
            )
        ]
        self.client.upsert(collection_name="documents", points=points)

    @step(output_name="search_results")
    async def search(
        self,
        query_embedding: list[list[float]],
    ) -> list[InMemorySearchResult]:
        search_result: List[InMemorySearchResult] = []

        if len(self.files) == 0:
            # return the search results as ContentItem
            return search_result

        # Ensure query_vector is of the correct type
        query_vector: list[float] = query_embedding[0]

        search_filter = None
        # if file_names:
        #     search_filter = models.Filter(
        #         must=[
        #             models.FieldCondition(
        #                 key="file_name", match=models.MatchAny(any=file_names)
        #             )
        #         ]
        #     )

        # Perform the search
        # convert the query vector to a acceptable format

        client_search_results = self.client.search(
            collection_name="documents",
            query_vector=query_vector,
            limit=self.top_k,
            query_filter=search_filter,
        )
        # find the file names and chunk names

        for result in client_search_results:
            if result.payload is not None:
                file_name = result.payload["filename"]
                chunk_position = result.payload["chunk_position"]

                # get the file content and the chunk content
                file_obj = next(
                    (file for file in self.files if file["filename"] == file_name), None
                )
                if file_obj is None:
                    raise ValueError(f"File {file_name} not found")

                file_content = file_obj["filecontent"]
                chunk_content = file_content[chunk_position[0] : chunk_position[1]]

                # get the chunk score and sort the chunks by score
                chunk_score = result.score

                search_result.append(
                    InMemorySearchResult(
                        file_name=file_name,  # Use the alias as defined in the Field
                        content=file_content,
                        chunk_content=chunk_content,  # Ensure alias is used
                        score=chunk_score,  # Correct alias for score
                    )
                )

            else:
                raise ValueError("Payload is empty")

        # return the search results as ContentItem
        return search_result
