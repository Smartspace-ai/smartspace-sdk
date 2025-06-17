from typing import Annotated

from llama_index.core import Document
from llama_index.core.node_parser import (
    SemanticSplitterNodeParser,
)
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

from smartspace.core import Block, Config, Metadata, metadata, step
from smartspace.enums import BlockCategory


@metadata(
    category=BlockCategory.FUNCTION,
    description="Splits text into semantically related chunks using AI embeddings. Groups sentences by meaning rather than size for better context preservation. Use this for content that needs coherent meaning.",
    icon="fa-quote-left",
    label="semantic chunk, meaning-based split, context splitting, ai chunking, smart divide",
)
class SemanticChunk(Block):
    buffer_size: Annotated[int, Config(), Metadata(description="Number of sentences to group for similarity evaluation.")] = 1

    breakpoint_percentile_threshold: Annotated[int, Config(), Metadata(description="Percentile threshold for semantic break detection.")] = 95

    model_name: Annotated[str, Config(), Metadata(description="Embedding model for semantic similarity.")] = "BAAI/bge-small-en-v1.5"

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
