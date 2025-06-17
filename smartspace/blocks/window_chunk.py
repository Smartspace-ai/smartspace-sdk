from typing import Annotated

from llama_index.core import Document
from llama_index.core.node_parser import (
    SentenceWindowNodeParser,
)

from smartspace.core import Block, Config, Metadata, metadata, step
from smartspace.enums import BlockCategory


@metadata(
    category=BlockCategory.FUNCTION,
    description="Creates overlapping text chunks with surrounding sentence context. Each chunk includes neighboring sentences for better context preservation. Use this for analysis requiring sentence relationships.",
    icon="fa-window-maximize",
    label="window chunk, context chunk, surrounding sentences, overlapping chunks, sentence context",
)
class WindowChunk(Block):
    # Sentence Chunking
    window_size: Annotated[int, Config(), Metadata(description="Number of surrounding sentences to include.")] = 3

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
