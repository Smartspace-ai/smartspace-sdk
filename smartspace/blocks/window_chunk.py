from typing import Annotated

from llama_index.core import Document
from llama_index.core.node_parser import (
    SentenceWindowNodeParser,
)

from smartspace.core import Block, Config, metadata, step
from smartspace.enums import BlockCategory


@metadata(
    category=BlockCategory.FUNCTION,
    description="""
    Sentence window chunk parser.

    Splits a document into Chunks
    Each chunk contains a window from the surrounding sentences.

    Args:
        window_size: The number of sentences on each side of a sentence to capture.
    """,
)
class WindowChunk(Block):
    # Sentence Chunking
    window_size: Annotated[int, Config()] = 3

    @step(output_name="result")
    async def window_chunk(self, text: str | list[str]) -> list[str]:
        if isinstance(text, str):
            doc_text_list = [text]
        else:
            doc_text_list = text

        documents = [Document(text=doc_text) for doc_text in doc_text_list]

        splitter = SentenceWindowNodeParser.from_defaults(
            window_size=self.window_size,
            window_metadata_key="window",
            original_text_metadata_key="original_sentence",
        )

        try:
            nodes = splitter.get_nodes_from_documents(documents)
            text_chunks = [node.metadata["window"] for node in nodes]
            if len(text_chunks) == 0:
                text_chunks = [
                    ""
                ]  # there is not sentence to chunk, therefore the result is empty
            return text_chunks
        except Exception as e:
            raise RuntimeError(f"Error during chunking: {str(e)}")
