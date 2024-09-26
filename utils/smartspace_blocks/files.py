from typing import IO, cast

import nltk
from injector import inject
from smartspace.core import (
    Block,
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
