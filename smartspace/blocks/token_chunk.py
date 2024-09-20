from typing import Annotated

import tiktoken
from llama_index.core import Document
from llama_index.core.node_parser import (
    TokenTextSplitter,
)
from tiktoken.model import MODEL_TO_ENCODING
from transformers import AutoTokenizer

from smartspace.core import Block, Config, metadata, step
from smartspace.enums import BlockCategory


@metadata(
    category=BlockCategory.FUNCTION,
    description="""
    Parse the document text into chunks with a fixed token size.

    Args:
    - chunk_size: The number of tokens to include in each chunk. (default is 200)
    - chunk_overlap: The number of tokens that overlap between consecutive
                        chunks. (default is 10)
    - separator: Default separator for splitting into words. (default is " ")

    This chunking method is particularly useful when:
    - You need precise control over the size of each chunk.
    - You're working with models that have specific token limits.
    - You want to ensure consistent chunk sizes across different types of text.

    Note: While this method provides consistent chunk sizes, it may split sentences
    or even words, which could affect the coherence of each chunk. Consider the
    trade-off between consistent size and semantic coherence when using this method.
    """,
)
class TokenChunk(Block):
    chunk_size: Annotated[int, Config()] = 200
    chunk_overlap: Annotated[int, Config()] = 10
    separator: Annotated[str, Config()] = " "
    model_name: Annotated[str, Config()] = "gpt-3.5-turbo"

    # backup_separators: Annotated[List] # description="Additional separators for splitting."

    @step(output_name="result")
    async def token_chunk(self, text: str | list[str]) -> list[str]:
        # get the tokenizer for the model
        tiktoken_models = MODEL_TO_ENCODING.keys()

        if self.model_name in tiktoken_models:
            tokenizer = tiktoken.encoding_for_model(model_name=self.model_name).encode
        else:
            try:
                tokenizer = AutoTokenizer.from_pretrained(self.model_name).encode
            except Exception as e:
                raise RuntimeError(
                    f"Error loading tokenizer for model {self.model_name}: {str(e)}"
                )
        # for single document, convert to list
        if isinstance(text, str):
            doc_text_list = [text]
        else:
            doc_text_list = text
        documents = [Document(text=doc_text) for doc_text in doc_text_list]
        splitter = TokenTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            tokenizer=tokenizer,
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
