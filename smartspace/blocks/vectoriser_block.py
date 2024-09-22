from typing import List

from llama_index.embeddings.huggingface import HuggingFaceEmbedding

from smartspace.core import Block, Config, metadata, step
from smartspace.enums import BlockCategory


@metadata(
    category=BlockCategory.FUNCTION,
    description="""
    Vectorise chunks of text into embeddings.

    Args:
        model_name: The name of the embedding model to use.

    Steps:
        1: Create embeddings for the input chunks.

    """,
)
class Vectoriser(Block):
    emb_model_name: Config[str] = "BAAI/bge-small-en-v1.5"

    embed_model = HuggingFaceEmbedding(model_name=emb_model_name)

    @step(output_name="embeddings")
    async def vectorise(self, input: str | list[str]) -> List[List[float]]:
        if isinstance(input, str):
            input = [input]

        embeddings = self.embed_model.get_text_embedding_batch(input)
        return embeddings
