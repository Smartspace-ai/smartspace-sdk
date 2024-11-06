from typing import Annotated

from injector import inject
from llama_index.core import Document
from llama_index.core.node_parser import (
    SemanticSplitterNodeParser,
)
from llama_index.core.schema import TextNode
from smartspace.core import Block, Config, metadata, step
from smartspace.enums import BlockCategory

from app.blocks.native.files_blocks.models import Chunk
from app.blocks.native.files_blocks.smartspace_base_embedding import (
    SmartSpaceBaseEmbedding,
)
from app.integrations.embeddings.core import DefaultEmbeddingsService


@metadata(
    category=BlockCategory.FUNCTION,
    description="""
    Semantic chunk parser.

    Splits a document into Chunks, with each node being a group of semantically related sentences.

    Args:
        buffer_size (int): number of sentences to group together when evaluating semantic similarity
        breakpoint_percentile_threshold: (int): the percentile of cosine dissimilarity that must be exceeded between a group of sentences and the next to form a node. The smaller this number is, the more nodes will be generated
    """,
)
class SemanticChunk(Block):
    buffer_size: Annotated[int, Config()] = 1

    breakpoint_percentile_threshold: Annotated[int, Config()] = 95

    @inject
    def __init__(
        self,
        embeddings_service: DefaultEmbeddingsService,
    ):
        super().__init__()
        self.embeddings_service = embeddings_service

    @step(output_name="result")
    async def semantic_chunk(self, text: str | list[str]) -> list[Chunk]:
        if isinstance(text, str):
            doc_text_list = [text]
        else:
            doc_text_list = text

        documents = [Document(text=doc_text) for doc_text in doc_text_list]

        embed_model = SmartSpaceBaseEmbedding(self.embeddings_service)

        splitter = SemanticSplitterNodeParser(
            buffer_size=self.buffer_size,
            breakpoint_percentile_threshold=self.breakpoint_percentile_threshold,
            embed_model=embed_model,
        )

        try:
            nodes = await splitter.aget_nodes_from_documents(documents)
            text_chunks: list[Chunk] = []
            position = 0
            index = 0

            for node in nodes:
                if isinstance(node, TextNode):
                    chunk = Chunk(
                        name="", content=node.text or "", position=position, index=index
                    )
                    text_chunks.append(chunk)
                    index += 1
                    position += len(chunk.content)

            return text_chunks
        except Exception as e:
            raise RuntimeError(f"Error during chunking: {str(e)}")
