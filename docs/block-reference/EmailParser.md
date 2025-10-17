{% set path = "assets/" + page.title + "-block.png" %}
{% if block_image_exists(path) %}
![{{page.title}}]({{path}}){{ block_image_sizing() }}
{% endif %}

## Overview

Extracts structured data from email files including sender, recipients, subject, body, and attachments. Supports Microsoft Outlook `.msg` and standard `.eml` formats with configurable extraction of extended metadata fields. Automatically uploads attachments to blob storage and returns them as File objects. Useful for email ingestion pipelines, automated email processing, and communication analysis workflows.

## Description

Parses email files and extracts relevant information. Supports MSG and EML files.


## Metadata

- **Category**: Function
- **Label**: email parser

## Configuration Options

| Name | Data Type | Description | Default Value |
|------|-----------|-------------|---------------|
| extras | `Dict[str, EmailContentOption]` | Optional extra fields to emit (e.g., `bcc`, `reply_to`, `meeting fields`) | `{}` |

## Inputs

| Name | Data Type | Description |
|------|-----------|-------------|
| file | `File` | Email file to parse (`.msg` or `.eml`) |

## Outputs

| Name | Data Type | Description |
|------|-----------|-------------|
| conversation_topic | `str` | Email conversation topic (when present) |
| conversation_index | `str` | Conversation index (when present) |
| flags | `Dict[str, Any]` | Flags metadata (e.g., follow-up) |
| categories | `List[str]` | Outlook categories |
| importance | `int` | Importance value |
| sensitivity | `str` | Sensitivity label |
| attachments | `List[File]` | Uploaded attachment files (stored via blob service) |
| cc | `List[str]` | CC recipients |
| to | `List[str]` | TO recipients |
| date | `str` | Sent date/time (string) |
| subject | `str` | Subject line |
| body | `str` | Body text (plain text) |
| sender | `str` | Sender address |

## State Variables

No state variables available.



## Example(s)
### Example 1: Parse a .eml file
- Input: `File(id="...", name="message.eml")`
- Outputs include `sender`, `to`, `cc`, `subject`, `date`, `body`, and `attachments` (if any).

### Example 2: Parse a .msg file with extras
- Configure `extras` to include additional fields (e.g., `bcc`, `reply_to`).
- Input: `File(id="...", name="meeting.msg")`
- Outputs include the standard fields plus any requested extras when available in the MSG.

## Error Handling
 - If the file cannot be parsed as a supported email type, the block will raise a parse error.
 - Attachments are uploaded individually; invalid attachment entries are skipped.

## FAQ
???+ question "What email types are supported?"

    Microsoft Outlook `.msg` and standard `.eml` files are supported.

???+ question "How are attachments handled?"

    Attachments are uploaded to blob storage and returned as `File` objects.

???+ question "What do extras do?"

    `extras` enables additional MSG-only fields (like `bcc`, `reply_to`, meeting times, attendees) to be emitted when present.

