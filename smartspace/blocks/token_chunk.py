from typing import Annotated

import tiktoken
from llama_index.core import Document
from llama_index.core.node_parser import (
    TokenTextSplitter,
)
from tiktoken.model import MODEL_TO_ENCODING
from transformers import AutoTokenizer

from smartspace.core import Block, Config, Metadata, metadata, step
from smartspace.enums import BlockCategory


@metadata(
    category=BlockCategory.FUNCTION,
    description="Splits text into fixed-size token chunks regardless of sentence boundaries. Provides precise control over chunk size for AI model processing. Use this when exact token limits are required.",
    icon="fa-tags",
    label="token chunk, fixed size, token split, precise chunking, model limits",
)
class TokenChunk(Block):
    chunk_size: Annotated[int, Config(), Metadata(description="Maximum tokens per chunk.")] = 200
    chunk_overlap: Annotated[int, Config(), Metadata(description="Token overlap between consecutive chunks.")] = 10
    separator: Annotated[str, Config(), Metadata(description="Word separator for text splitting.")] = " "
    model_name: Annotated[str, Config(), Metadata(description="Tokenizer model for token counting.")] = "gpt-3.5-turbo"

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
