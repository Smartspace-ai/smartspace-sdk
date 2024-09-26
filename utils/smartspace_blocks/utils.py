import base64
from typing import Any

from smartspace.models import ContentItem, ThreadMessage

from app.integrations.blob_storage.core import BlobService
from app.integrations.llms.models import (
    AssistantMessage,
    MessageTypes,
    SystemMessage,
    UserMessageContentList,
)


async def prepare_chat_history(
    pre_prompt: str | None,
    thread_history: list[ThreadMessage] | None,
    blob_service: BlobService,
) -> list[MessageTypes]:
    message_history: list[MessageTypes] = []

    if pre_prompt:
        message_history.append(SystemMessage(content=pre_prompt))

    if thread_history:
        for message in sorted(thread_history, key=lambda m: m.created_at):
            message_history.append(
                UserMessageContentList(
                    content=await get_message_from_content_list(
                        message.content or message.content_list or [], blob_service
                    )
                )
            )
            message_history.append(AssistantMessage(content=message.response.content))

    return message_history


async def get_message_from_content_list(
    content: list[ContentItem] | str,
    blob_service: BlobService,
):
    results: list[dict[str, Any]] = []

    if isinstance(content, str):
        return [
            {
                "type": "text",
                "text": content,
            }
        ]

    for item in content:
        if item.text is not None:
            results.append(
                {
                    "type": "text",
                    "text": item.text,
                }
            )

        elif item.image is not None:
            blob = await blob_service.get_blob(item.image.uri)
            data_bytes = blob.bytes.read()
            data_base64 = base64.b64encode(data_bytes)
            results.append(
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{data_base64.decode()}"
                    },
                }
            )

    return results
