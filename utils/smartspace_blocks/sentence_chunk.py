from typing import Annotated

from injector import inject
from llama_index.core import Document
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.schema import TextNode
from pydantic import Field
from smartspace.core import Block, Config, Output, metadata, step
from smartspace.enums import BlockCategory

from app.blocks.native.files_blocks.models import Chunk
from app.integrations.embeddings.core import DefaultEmbeddingsService


@metadata(
    category=BlockCategory.FUNCTION,
    description="""
    Parse text with a preference for complete sentences and track chunk positions.
    This class keeps sentences and paragraphs together while providing the position
    of each chunk in the original text.
    
    Args:
        chunk_size: The number of tokens to include in each chunk. (default is 200)
        chunk_overlap: The number of tokens that overlap between consecutive chunks. (default is 10)
        separator: Default separator for splitting into words. (default is " ")
        paragraph_separator: Separator between paragraphs. (default is "\\n\\n\\n")
        secondary_chunking_regex: Backup regex for splitting into sentences. (default is "[^,\\.;]+[,\\.;]?".)
        
    Steps: 
        1: Break text into splits that are smaller than chunk size based on the separators and regex.
        2: Combine splits into chunks of size chunk_size (smaller than).
        3: Track the start and end positions of each chunk in the original text.
    """,
)
class SentenceChunk(Block):
    chunk_size: Annotated[int, Config()] = 200
    chunk_overlap: Annotated[
        int,
        Field(
            default=10,
            ge=0,  # Min value
            le=100,  # Max value
            multiple_of=1,  # Interval
        ),
        Config(),
    ]
    separator: Annotated[str, Config()] = " "
    paragraph_separator: Annotated[str, Config()] = "\n\n\n"
    secondary_chunking_regex: Annotated[str, Config()] = "[^,.;。？！]+[,.;。？！]?"

    chunks: Output[list[Chunk]]

    @inject
    def __init__(self, embeddings_service: DefaultEmbeddingsService):
        super().__init__()
        self.embeddings_service = embeddings_service

    @step()
    async def sentence_chunk(self, text: str | list[str]):
        if isinstance(text, str):
            doc_text_list = [text]
        else:
            doc_text_list = text

        documents = [Document(text=doc_text) for doc_text in doc_text_list]
        splitter = SentenceSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separator=self.separator,
            paragraph_separator=self.paragraph_separator,
            secondary_chunking_regex=self.secondary_chunking_regex,
        )

        try:
            nodes = splitter.get_nodes_from_documents(documents)

            chunks: list[Chunk] = []
            current_position = 0
            chunk_index = 0

            for doc_text in doc_text_list:
                doc_nodes = [
                    node
                    for node in nodes
                    if isinstance(node, TextNode) and node.text in doc_text
                ]
                for node in doc_nodes:
                    chunk_text = node.text or ""
                    start_pos = current_position
                    end_pos = start_pos + len(chunk_text)
                    chunks.append(
                        Chunk(
                            content=chunk_text,
                            name="",
                            index=chunk_index,
                            position=start_pos,
                        )
                    )
                    current_position = end_pos
                    chunk_index += 1

            if not chunks:
                chunks = []

            # use emit to return multiple value
            self.chunks.send(chunks)

        except Exception as e:
            raise RuntimeError(f"Error during chunking: {str(e)}")
