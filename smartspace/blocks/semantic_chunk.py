from typing import Annotated

from llama_index.core import Document
from llama_index.core.node_parser import (
    SemanticSplitterNodeParser,
)
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

from smartspace.core import Block, Config, metadata, step
from smartspace.enums import BlockCategory


@metadata(
    category=BlockCategory.FUNCTION,
    description="""
    Semantic chunk parser.

    Splits a document into Chunks, with each node being a group of semantically related sentences.

    Args:
        buffer_size (int): number of sentences to group together when evaluating semantic similarity
        chunk_model: (BaseEmbedding): embedding model to use, defaults to BAAI/bge-small-en-v1.5
        breakpoint_percentile_threshold: (int): the percentile of cosine dissimilarity that must be exceeded between a group of sentences and the next to form a node. The smaller this number is, the more nodes will be generated
    """,
)
class SemanticChunk(Block):
    buffer_size: Annotated[int, Config()] = 1

    breakpoint_percentile_threshold: Annotated[int, Config()] = 95

    model_name: Annotated[str, Config()] = "BAAI/bge-small-en-v1.5"

    @step(output_name="result")
    async def semantic_chunk(self, text: str | list[str]) -> list[str]:
        if isinstance(text, str):
            doc_text_list = [text]
        else:
            doc_text_list = text

        documents = [Document(text=doc_text) for doc_text in doc_text_list]

        embed_model = HuggingFaceEmbedding(model_name=self.model_name)

        splitter = SemanticSplitterNodeParser(
            buffer_size=self.buffer_size,
            breakpoint_percentile_threshold=self.breakpoint_percentile_threshold,
            embed_model=embed_model,
        )

        try:
            nodes = splitter.get_nodes_from_documents(documents)
            text_chunks = [node.text for node in nodes]
            if len(text_chunks) == 0:
                text_chunks = [""]
            return text_chunks
        except Exception as e:
            raise RuntimeError(f"Error during chunking: {str(e)}")
