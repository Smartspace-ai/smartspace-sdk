{% set path = "assets/" + page.title + "-block.png" %}
{% if block_image_exists(path) %}
![{{page.title}}]({{path}}){{ block_image_sizing() }}
{% endif %}

## Overview

Enforces structured JSON output from an LLM by providing a dynamic JSON schema at runtime. Unlike the standard LLM block with fixed output schema, this block accepts the schema as an input parameter, enabling flexible structured generation. Automatically uses tool/function calling to guarantee schema compliance when supported by the model.

## Description

Guides an LLM to respond according to a specific JSON schema.

Notes:
- Schema is provided as an input (not configuration), allowing dynamic schema definition per call
- Automatically wraps non-object schemas in `{"response": <schema>}` for tool calling
- Falls back to free-form text if schema type is "string" or unspecified
- Uses tool calling with "required" choice to enforce schema compliance when model supports it
- Supports conversation history via `use_thread_history` for context-aware structured generation

## Metadata

- **Category**: Agent
- **Label**: schema guided llm, structured output generation, json response generation, controlled llm output

## Configuration Options

| Name | Data Type | Description | Default Value |
|------|-----------|-------------|---------------|
| llm_config | `ModelConfig` | Language model configuration including model name, temperature, and pre-prompt | (required) |
| use_thread_history | `bool` | Include conversation history when generating structured output | (required) |

## Inputs

| Name | Data Type | Description |
|------|-----------|-------------|
| message | `list[ContentItem] or ContentItem or str` | User message(s) to process - can be text, single content item, or list of content items |
| response_schema | `dict[str, Any]` | JSON schema defining expected output structure (provided dynamically per call) |

## Outputs

| Name | Data Type | Description |
|------|-----------|-------------|
| response | `Any` | Structured output conforming to the provided schema (or string if schema type is "string") |

## State Variables

No state variables available.



## Example(s)

### Example 1: Extract structured product information
- Config: `use_thread_history=False`
- Input message: `"The Galaxy S24 costs $899 with 256GB storage and 5G support"`
- Input schema: `{"type": "object", "properties": {"product": {"type": "string"}, "price": {"type": "number"}, "features": {"type": "array", "items": {"type": "string"}}}}`
- Output: `{"product": "Galaxy S24", "price": 899, "features": ["256GB storage", "5G support"]}`

### Example 2: Simple field extraction with wrapper
- Input message: `"The meeting is scheduled for Tuesday at 3 PM"`
- Input schema: `{"type": "string", "enum": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]}`
- Output: `"Tuesday"` (wrapped internally as `{"response": "Tuesday"}` for tool calling)

### Example 3: Context-aware structured response
- Config: `use_thread_history=True`
- Previous messages in history: User discusses a software project
- Input message: `"What are the key milestones?"`
- Input schema: `{"type": "object", "properties": {"milestones": {"type": "array", "items": {"type": "object", "properties": {"name": {"type": "string"}, "date": {"type": "string"}}}}}}`
- Output: Structured milestones based on previous context

### Example 4: Free-form text with string schema
- Input message: `"Explain quantum computing"`
- Input schema: `{"type": "string"}`
- Output: Free-form text explanation (no tool calling, direct LLM response)

## Error Handling

- If the LLM returns empty arguments for the tool call, raises `BlockError` with the empty data
- If tool calling fails, falls back to free-form response (string content)
- Token limit exceeded: request is automatically truncated via `remove_excess_tokens_chat_request`
- Invalid schema format: errors during tool call setup will propagate

## FAQ

???+ question "How does this differ from the LLM block with output_schema?"

    - **SchemaGuidedLLM**: Schema is an input parameter, allowing dynamic schemas per call
    - **LLM with output_schema**: Schema is configuration, fixed at block creation time
    
    Use SchemaGuidedLLM when you need different schemas for different messages.

???+ question "What happens if the model doesn't support tool calling?"

    The block will fall back to a standard chat completion request, but structured output is not guaranteed. Use models that support function/tool calling for reliable structured generation.

???+ question "Can I use complex nested schemas?"

    Yes, any valid JSON schema is supported, including nested objects, arrays, enums, and all standard JSON schema features.

???+ question "Why wrap non-object schemas?"

    Tool calling typically expects an object schema. The block automatically wraps non-object schemas in `{"response": <schema>}` for tool calling, then unwraps the result.

???+ question "How do I get free-form text responses?"

    Use `{"type": "string"}` as the schema, or omit the "type" field. The block will use standard chat completion without tool calling.

