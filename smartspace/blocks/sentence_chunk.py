from typing import Annotated

import tiktoken
from llama_index.core import Document
from llama_index.core.node_parser import (
    SentenceSplitter,
)
from tiktoken.model import MODEL_TO_ENCODING
from transformers import AutoTokenizer

from smartspace.core import Block, Config, Metadata, metadata, step
from smartspace.enums import BlockCategory


@metadata(
    category=BlockCategory.FUNCTION,
    description="Splits text into chunks while preserving complete sentences. Maintains sentence integrity and paragraph structure for better readability. Use this for content requiring natural language flow.",
    icon="fa-paragraph",
    label="sentence chunk, preserve sentences, smart split, readable chunks, text segmentation",
)
class SentenceChunk(Block):
    chunk_size: Annotated[int, Config(), Metadata(description="Maximum tokens per chunk.")] = 200
    chunk_overlap: Annotated[int, Config(), Metadata(description="Token overlap between consecutive chunks.")] = 10

    separator: Annotated[str, Config(), Metadata(description="Word separator for text splitting.")] = " "
    paragraph_separator: Annotated[str, Config(), Metadata(description="Separator between paragraphs.")] = "\n\n\n"
    model_name: Annotated[str, Config(), Metadata(description="Tokenizer model for token counting.")] = "gpt-3.5-turbo"

    secondary_chunking_regex: Annotated[str, Config(), Metadata(description="Regex pattern for sentence splitting.")] = "[^,.;。？！]+[,.;。？！]?"

    @step(output_name="result")
    async def sentence_chunk(self, text: str | list[str]) -> list[str]:
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
