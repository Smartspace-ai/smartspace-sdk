from typing import Annotated, Dict, List

import tiktoken
from llama_index.core import Document
from llama_index.core.node_parser import SentenceSplitter
from tiktoken.model import MODEL_TO_ENCODING
from transformers import AutoTokenizer

from smartspace.core import Block, Config, metadata, step
from smartspace.enums import BlockCategory


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
class SentenceChunkPOS(Block):
    chunk_size: Annotated[int, Config()] = 200
    chunk_overlap: Annotated[int, Config()] = 10

    separator: Annotated[str, Config()] = " "
    paragraph_separator: Annotated[str, Config()] = "\n\n\n"
    llm_name: Annotated[str, Config()] = "gpt-2"  # "allenai/longformer-base-4096"

    secondary_chunking_regex: Annotated[str, Config()] = "[^,.;。？！]+[,.;。？！]?"

    tiktoken_models = MODEL_TO_ENCODING.keys()

    if llm_name in tiktoken_models:
        tokenizer = tiktoken.encoding_for_model(model_name=llm_name).encode
    else:
        try:
            tokenizer = AutoTokenizer.from_pretrained(llm_name).encode
        except Exception as e:
            raise RuntimeError(
                f"Error loading tokenizer for model {llm_name}: {str(e)}"
            )

    # chunks: Output[List[str]]``
    # chunk_positions: Output[List[tuple[int, int]]]

    @step(output_name="chunks")
    async def sentence_chunk_debug(self, text: str | List[str]) -> List[Dict]:
        # tiktoken_models = MODEL_TO_ENCODING.keys()

        # if self.llm_name in tiktoken_models:
        #     tokenizer = tiktoken.encoding_for_model(model_name=self.llm_name).encode
        # else:
        #     try:
        #         tokenizer = AutoTokenizer.from_pretrained(self.llm_name).encode
        #     except Exception as e:
        #         raise RuntimeError(
        #             f"Error loading tokenizer for model {self.llm_name}: {str(e)}"
        #         )
        # tokenizer = self.tokenizer
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
            tokenizer=self.tokenizer,
        )

        try:
            nodes = splitter.get_nodes_from_documents(documents)

            chunks: List[Dict] = []
            chunk_positions = []
            current_position = 0

            for doc_text in doc_text_list:
                doc_nodes = [node for node in nodes if node.text in doc_text]
                for idx, node in enumerate(doc_nodes):
                    chunk_text = node.text
                    start_pos = current_position
                    end_pos = start_pos + len(chunk_text)
                    # chunks.append(chunk_text)
                    chunk_positions.append((start_pos, end_pos))
                    current_position = end_pos

                    chunks.append(
                        {"text": chunk_text, "position": (start_pos, end_pos)}
                    )

            # if not chunks:
            #     chunks = [""]
            #     chunk_positions = [(0, 0)]  # 如果没有块，返回空结果
            # use emit to return multiple value
            # self.chunks.send(chunks)
            # self.chunk_positions.send(chunk_positions)
            return chunks

        except Exception as e:
            raise RuntimeError(f"Error during chunking: {str(e)}")
