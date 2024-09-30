import warnings
from typing import Annotated, List

from llama_index.embeddings.huggingface import HuggingFaceEmbedding

from smartspace.core import Block, Config, metadata, step
from smartspace.enums import BlockCategory

warnings.filterwarnings("ignore")


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
class QueryVectoriserDebug(Block):
    emb_model_name: Annotated[str, Config()] = "BAAI/bge-small-en-v1.5"

    embed_model = HuggingFaceEmbedding(model_name=emb_model_name)

    @step(output_name="embeddings")
    async def vectorise(self, input_text: str | list[str]) -> List[List[float]]:
        if isinstance(input_text, str):
            input_text_list = [input_text]
        else:
            input_text_list = input_text

        embeddings = []

        for text in input_text_list:
            text_embeddings = self.embed_model.get_text_embedding(text)
            embeddings.append(text_embeddings)

        return embeddings
