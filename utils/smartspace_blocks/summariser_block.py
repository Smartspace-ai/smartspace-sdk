# # block warnings
# import warnings
# from typing import Annotated, List

# import torch
# from llama_index.core import PromptTemplate
# from llama_index.llms.huggingface import HuggingFaceLLM
# from smartspace.core import Block, Config, metadata, step
# from smartspace.enums import BlockCategory
# from smartspace.models import ContentItem, InMemorySearchResult, SearchResult
# from transformers import AutoConfig, AutoTokenizer

# warnings.filterwarnings("ignore")


# @metadata(
#     category=BlockCategory.FUNCTION,
#     description="""
#     Summarize documents or chunks of text using llama_index with Hugging Face models.

#     Args:
#         llm_model_name: The name of the Hugging Face LLM to use for summarization.
#         embedding_model_name: The name of the Hugging Face embedding model to use for tokenization.
#         max_tokens: The maximum number of tokens for the LLM context.

#     Steps:
#         1: Check if the entire document fits within token limits.
#         2: If it fits, summarize the full document.
#         3: If not, perform progressive summarization on chunks.

#     """,
# )
# class Summariser(Block):
#     llm_name: Annotated[str, Config()] = "HuggingFaceH4/tiny-random-LlamaForCausalLM"
#     tokenizer_name: Annotated[str, Config()] = (
#         "HuggingFaceH4/tiny-random-LlamaForCausalLM"
#     )
#     context_window: Annotated[int, Config()] = 2048
#     max_new_tokens: Annotated[int, Config()] = 256

#     temperature: Annotated[float, Config()] = 0.7
#     top_k: Annotated[int, Config()] = 50
#     top_p: Annotated[float, Config()] = 0.95

#     # Determine the device map based on the model type
#     if torch.cuda.is_available():
#         device_map = "auto"  # Use GPU if available
#     else:
#         device_map = "cpu"  # Fallback to CPU

#     # Load the model configuration
#     config = AutoConfig.from_pretrained(llm_name)
#     # Retrieve the maximum number of tokens the model can handle
#     max_tokens = config.max_position_embeddings

#     # Check if the context_window exceeds the max_tokens
#     if context_window > max_tokens:
#         print(
#             f"Info: context_window ({context_window}) exceeds the limitation ({max_tokens}) for {llm_name}. Using the maximum number of tokens instead."
#         )
#         context_window = max_tokens

#     tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)

#     llm = HuggingFaceLLM(
#         model_name=llm_name,
#         tokenizer_name=tokenizer_name,
#         context_window=context_window,
#         max_new_tokens=max_new_tokens,
#         generate_kwargs={
#             "temperature": temperature,
#             "top_k": top_k,
#             "top_p": top_p,
#         },
#         device_map=device_map,
#     )

#     @step(output_name="summary")
#     async def summarize(
#         self, documents: List[InMemorySearchResult], message: List[ContentItem]
#     ) -> SearchResult:
#         # check all file_name, file_content, chunk_content of the documents and the message text
#         if any(doc.file_name is None for doc in documents):
#             return SearchResult(content="Document names are missing.", score=0)
#         if any(doc.content is None for doc in documents):
#             return SearchResult(content="Document content is missing.", score=0)
#         if any(doc.chunk_content is None for doc in documents):
#             return SearchResult(content="Document chunk content is missing.", score=0)
#         if not message or len(message) == 0:
#             return SearchResult(content="No message provided.", score=0)
#         if not message[0].text:
#             return SearchResult(content="Message text is missing.", score=0)

#         # using the self.llm to detect whether the message specified document names to answer the question. If specified, get the file names from all_file_names
#         # message_text = message[0].text
#         # all_file_names = [doc.file_name for doc in documents]

#         # specified_file_prompt = await self._create_doc_selction_prompt(
#         #     message_text, all_file_names
#         # )
#         # response = await self.llm.acomplete(specified_file_prompt)

#         # specified_file_names = eval(
#         #     response.text.strip()
#         # )  # convert the string to a list of file names

#         # specified_docs = [
#         #     doc for doc in documents if doc.file_name in specified_file_names
#         # ]

#         specified_docs = documents
#         specified_file_names = [doc.file_name for doc in documents]

#         if len(specified_file_names) > 0:
#             all_doc_content = " \n ".join(
#                 list(set([doc.content for doc in specified_docs]))
#             )

#             all_chunks = [
#                 doc.chunk_content for doc in specified_docs if doc.chunk_content
#             ]
#             all_chunk_scores = [doc.score for doc in specified_docs]

#             # Sort the chunks based on the scores in descending order to prioritize the most relevant chunks
#             sorted_chunks = [
#                 chunk
#                 for _, chunk in sorted(zip(all_chunk_scores, all_chunks), reverse=True)
#             ]

#             tokens = self.tokenizer.encode(all_doc_content)

#             if len(tokens) <= self.context_window:
#                 sum_text = await self._summarize_full(all_doc_content)
#             else:
#                 sum_text = await self._progressive_summarize(sorted_chunks)
#         elif len(specified_file_names) == 0:
#             sum_text = "No document names specified in the message."

#         return SearchResult(content=sum_text, score=1)

#     async def _summarize_full(self, content: str) -> str:
#         prompt_template = PromptTemplate(
#             "Please summarize the following document:\n\n{text}\n\nSummary:"
#         )
#         prompt = prompt_template.format(text=content)
#         response = self.llm.complete(prompt)
#         return response.text

#     async def _create_doc_selction_prompt(
#         self, message_text: str, file_names: List[str]
#     ) -> str:
#         file_name_str = ", ".join(file_names)
#         prompt = f"""
#         You are an intelligent assistant. Your task is to analyze the following message and determine if it specifies any document names. If document names are specified, list them. If no document names are specified, return an empty list.

#         Message:
#         "{message_text}"
#         Available document names:
#         {file_name_str}
#         Instructions:
#         1. Identify any document names mentioned in the message.
#         2. Return a list of the document names mentioned.
#         3. If no document names are mentioned, return an empty list.

#         Example:
#         Message: "Please refer to document1 and document2 for more details."
#         Output: ["document1", "document2"]

#         Message: "I need information about the project."
#         Output: []

#         Now, analyze the given message and provide the output.
#         """
#         return prompt

#     async def _progressive_summarize(self, chunks: list[str]) -> str:
#         summaries = []

#         for chunk in chunks:
#             chunk_summary = await self._summarize_full(chunk)
#             summaries.append(chunk_summary)

#         combined_summary = " ".join(summaries)
#         final_summary = await self._summarize_full(combined_summary)
#         return final_summary
