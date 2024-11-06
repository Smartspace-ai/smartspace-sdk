import base64
from typing import IO, Annotated, cast

import nltk
from injector import inject
from smartspace.core import (
    Block,
    Config,
    Metadata,
    Output,
    metadata,
    step,
)
from smartspace.enums import BlockCategory
from smartspace.models import File
from unstructured.documents.elements import Element  # type: ignore
from unstructured.file_utils.filetype import (
    FileType,
    detect_filetype,
)
from unstructured.partition.auto import partition  # type: ignore
from unstructured.staging.base import convert_to_text  # type: ignore

from app.integrations.blob_storage.core import BlobService
from app.integrations.blob_storage.models import Blob
from app.utils.pandoc import PandocToFormats, convert_document

nltk.download("punkt_tab")
nltk.download("averaged_perceptron_tagger_eng")


def extract_pdf_text(data: IO[bytes]) -> str:
    from pypdf import PdfReader

    reader = PdfReader(data)
    text: list[str] = []
    for page in reader.pages:
        text.append(page.extract_text())
    return "\n\n".join(text)


async def get_file_content(file: File, blob_service: BlobService) -> str:
    blob = await blob_service.get_blob(file.uri)
    data = blob.bytes
    filetype: FileType | None = detect_filetype(file=data)
    text = ""
    if filetype == FileType.PDF:
        # unstructured pdf text extraction extremely slow
        text = extract_pdf_text(data)
    else:
        # Reset pointer to beginning of file
        data.seek(0)
        elements = cast(list[Element], partition(file=data))
        text = convert_to_text(elements=elements)
    return text


@metadata(category=BlockCategory.DATA)
class GetFileContent(Block):
    content: Output[str]
    file_name: Output[str]

    @inject
    def __init__(
        self,
        blob_service: BlobService,
    ):
        super().__init__()

        self.blob_service = blob_service

    @step()
    async def get_file_content(self, file: File):
        file_content = await get_file_content(file, self.blob_service)
        self.content.send(file_content)
        self.file_name.send(file.name or "")


def get_file_bytes_string(blob: Blob) -> str:
    bytes_data = blob.bytes.read()
    # send string of bytes
    base64_string = base64.b64encode(bytes_data).decode("utf-8")
    return base64_string


@metadata(
    category=BlockCategory.DATA,
    description="Get's the raw file bytes of a file, saved as a base64 encoded string. Useful for custom processing.",
)
class GetFileBytes(Block):
    file_bytes_string: Annotated[
        Output[str], Metadata(description="Base64 encoded string of the file bytes")
    ]
    file_name: Annotated[Output[str], Metadata(description="Name of the file")]

    @inject
    def __init__(
        self,
        blob_service: BlobService,
    ):
        super().__init__()

        self.blob_service = blob_service

    @step()
    async def get_file_bytes(self, file: File):
        blob = await self.blob_service.get_blob(file.uri)
        base64_string = get_file_bytes_string(blob)
        self.file_bytes_string.send(base64_string)
        self.file_name.send(file.name or "")


@metadata(
    category=BlockCategory.DATA,
    description="Converts file content to another format using pandoc.",
)
class ConvertDocumentContent(Block):
    to_format: Annotated[PandocToFormats, Config()] = PandocToFormats.MARKDOWN
    output: Output[str]

    @inject
    def __init__(
        self,
        blob_service: BlobService,
    ):
        super().__init__()

        self.blob_service = blob_service

    @step()
    async def convert_document_content(self, file: File):
        blob = await self.blob_service.get_blob(file.uri)
        file_bytes_string = get_file_bytes_string(blob)
        converted_content = await convert_document(
            file_name=file.name or "",
            file_bytes=file_bytes_string,
            to_format=self.to_format,
        )
        self.output.send(converted_content)
