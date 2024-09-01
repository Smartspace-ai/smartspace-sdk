from llama_index.core import Document
from llama_index.core.node_parser import (
    SentenceSplitter,
)

from smartspace.core import Block, Config, metadata, step
from smartspace.enums import BlockCategory


@metadata(
    category=BlockCategory.FUNCTION,
    description="""
    Parse text with a preference for complete sentences.

    In general, this class tries to keep sentences and paragraphs together. Therefore
    compared to the original TokenTextSplitter, there are less likely to be
    hanging sentences or parts of sentences at the end of the node chunk.
    
    Args:
        chunk_size: The number of tokens to include in each chunk. (default is 200)
        chunk_overlap: The number of tokens that overlap between consecutive chunks. (default is 10)
        separator: Default separator for splitting into words. (default is " ")
        paragraph_separator: Separator between paragraphs. (default is "\\n\\n\\n")
        secondary_chunking_regex: Backup regex for splitting into sentences.(default is "[^,\\.;]+[,\\.;]?".)
        
    Steps: 
        1: Break text into splits that are smaller than chunk size base on the separators and regex.
        2: Combine splits into chunks of size chunk_size (smaller than).

    """,
)
class SentenceChunk(Block):
    chunk_size: Config[int] = 200
    chunk_overlap: Config[int] = 10

    separator: Config[str] = " "
    paragraph_separator: Config[str] = "\n\n\n"

    secondary_chunking_regex: Config[str] = "[^,.;。？！]+[,.;。？！]?"

    @step(output_name="result")
    async def sentence_chunk(self, text: str | list[str]) -> list[str]:
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
            text_chunks = [node.text for node in nodes]
            if len(text_chunks) == 0:
                text_chunks = [
                    ""
                ]  # there is not sentence to chunk, therefore the result is empty
            return text_chunks
        except Exception as e:
            raise RuntimeError(f"Error during chunking: {str(e)}")
