import json
import tempfile
from email import policy
from email.parser import BytesParser
from enum import Enum
from typing import Annotated, Any, Dict, List

from injector import inject
from msg_parser import MsOxMessage  # type: ignore
from smartspace.core import (
    Block,
    Config,
    Output,
    step,
)
from smartspace.models import File

from app.integrations.blob_storage.core import BlobService


def _load_json_map(raw_json):
    if isinstance(raw_json, dict):
        return raw_json
    if isinstance(raw_json, (memoryview, bytes, bytearray)):
        try:
            raw_json = (
                raw_json.tobytes() if isinstance(raw_json, memoryview) else raw_json
            )
            raw_json = raw_json.decode("utf-8")
        except Exception:
            return {}
    if isinstance(raw_json, str):
        try:
            return json.loads(raw_json)
        except Exception:
            return {}
    return {}


class EmailStandardField(str, Enum):
    sender = "sender"
    to = "to"
    cc = "cc"
    date = "date"
    subject = "subject"
    body = "body"
    flags = "flags"
    categories = "categories"
    importance = "importance"
    sensitivity = "sensitivity"
    conversation_topic = "conversation_topic"
    conversation_index = "conversation_index"
    attachments = "attachments"


class EmailExtraField(str, Enum):
    bcc = "bcc"
    reply_to = "reply_to"
    message_id = "message_id"
    header = "header"
    header_dict = "header_dict"
    sent_date = "sent_date"
    received_date = "received_date"
    created_date = "created_date"
    body_html = "body_html"
    body_rtf = "body_rtf"
    location = "location"
    start = "start"
    end = "end"
    attendees = "attendees"
    recipients = "recipients"
    has_attachments = "has_attachments"


class EmailContentOption:
    field: Annotated[EmailExtraField, Config()]
    output: Output[Any]


class EmailParser(Block):
    # Primary outputs with precise types

    conversation_topic: Output[str]
    conversation_index: Output[str]
    flags: Output[Dict[str, Any]]
    categories: Output[List[str]]
    importance: Output[int]
    sensitivity: Output[str]

    attachments: Output[List[File]]

    cc: Output[List[str]]
    to: Output[List[str]]
    date: Output[str]
    subject: Output[str]
    body: Output[str]
    sender: Output[str]

    # Dynamic extras configuration
    extras: Dict[str, EmailContentOption]

    @inject
    def __init__(self, blob_service: BlobService):
        super().__init__()
        self.blob_service = blob_service

    @step()
    async def run(self, file: File):
        # Retrieve .msg bytes and write to temp file
        file_data = await self.blob_service.get_file_content(file.id)
        raw = file_data.bytes.read()
        with tempfile.NamedTemporaryFile(suffix=".msg", delete=False) as tmp:
            tmp.write(raw)
            path = tmp.name

        # Parse message
        msg = MsOxMessage(path)

        # Load JSON-friendly map
        raw_json = msg.get_message_as_json()
        json_map = _load_json_map(raw_json)

        # Prepare standard outputs
        standard_outputs: list[tuple[Output[Any], Any]] = [
            (self.sender, msg.sender),
            (
                self.to,
                [
                    r.get("emailAddress", {}).get("address", "")
                    for r in json_map.get("to", [])
                ],
            ),
            (
                self.cc,
                [
                    r.get("emailAddress", {}).get("address", "")
                    for r in json_map.get("cc", [])
                ],
            ),
            (self.date, json_map.get("createdDateTime", "")),
            (self.subject, json_map.get("subject", "")),
            (self.body, json_map.get("body", {}).get("content", "")),
            (self.flags, json_map.get("flags", {})),
            (self.categories, json_map.get("categories", [])),
            (self.importance, int(json_map.get("importance", 0))),
            (self.sensitivity, json_map.get("sensitivity", "")),
            (self.conversation_topic, json_map.get("conversationTopic", "")),
            (self.conversation_index, json_map.get("conversationIndex", "")),
        ]
        for output_channel, value in standard_outputs:
            output_channel.send(value)

        # Handle attachments
        files_info: List[File] = []
        for attachment in msg.attachments:
            filename = attachment.Filename
            file_bytes = attachment.data
            uploaded_files = await self.blob_service.add_file([(filename, file_bytes)])
            files_info.append(uploaded_files[0])
        self.attachments.send(files_info)

        # Emit configured extras
        for extra in self.extras.values():
            extra.output.send(await self.get_extra_output(msg, extra.field))

    async def get_extra_output(
        self, msg: MsOxMessage, content_type: EmailExtraField
    ) -> Any:
        name = content_type.value

        raw_json = msg.get_message_as_json()
        json_map = _load_json_map(raw_json)

        # has_attachments flag
        if name == EmailExtraField.has_attachments.value:
            return bool(json_map.get("attachments", []))

        # JSON friendly fallback
        if name in json_map:
            return json_map.get(name)

        # Fallback to raw MAPI properties
        try:
            props = msg.get_properties()
            return props.get(name)
        except Exception:
            return None


def parse_eml(raw_bytes):
    msg = BytesParser(policy=policy.default).parsebytes(raw_bytes)
    sender = msg.get("from", "")
    to = msg.get_all("to", [])
    cc = msg.get_all("cc", [])
    bcc = msg.get_all("bcc", [])
    date = msg.get("date", "")
    subject = msg.get("subject", "")
    body, body_html = "", ""
    if msg.is_multipart():
        for part in msg.walk():
            ctype = part.get_content_type()
            if ctype in ("text/plain", "text/html"):
                payload = part.get_payload(decode=True)
                if isinstance(payload, bytes):
                    text = payload.decode(
                        part.get_content_charset() or "utf-8", errors="replace"
                    )
                    if ctype == "text/plain" and not body:
                        body = text
                    elif ctype == "text/html" and not body_html:
                        body_html = text
    else:
        ctype = msg.get_content_type()
        payload = msg.get_payload(decode=True)
        if isinstance(payload, bytes):
            text = payload.decode(
                msg.get_content_charset() or "utf-8", errors="replace"
            )
            if ctype == "text/plain":
                body = text
            elif ctype == "text/html":
                body_html = text
    attachments = [
        (part.get_filename(), part.get_payload(decode=True))
        for part in msg.walk()
        if part.get_filename()
    ]
    return {
        "sender": sender,
        "to": to,
        "cc": cc,
        "bcc": bcc,
        "date": date,
        "subject": subject,
        "body": body,
        "body_html": body_html,
        "attachments": attachments,
    }
