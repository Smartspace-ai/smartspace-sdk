from typing import Annotated

from llama_index.core import Document
from llama_index.core.node_parser import (
    SentenceWindowNodeParser,
)
from smartspace.core import Block, Config, metadata, step
from smartspace.enums import BlockCategory

from app.blocks.native.files_blocks.models import Chunk


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
    async def window_chunk(self, text: str | list[str]) -> list[Chunk]:
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
            text_chunks: list[Chunk] = []
            position = 0
            index = 0

            for node in nodes:
                chunk = Chunk(
                    name="",
                    content=node.metadata["window"],
                    position=position,
                    index=index,
                )
                text_chunks.append(chunk)
                position += len(chunk.content)
                index += 1

            return text_chunks
        except Exception as e:
            raise RuntimeError(f"Error during chunking: {str(e)}")
