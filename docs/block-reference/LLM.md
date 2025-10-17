{% set path = "assets/" + page.title + "-block.png" %}
{% if block_image_exists(path) %}
![{{page.title}}]({{path}}){{ block_image_sizing() }}
{% endif %}

## Overview
Conversation and structured output with optional tool calls and citations. Configure with a `ModelConfig` and a dynamic `response_schema` (string or JSON schema). Supports thread history, tool integration, and automatic source citation when dataset items are supplied.

{{ generate_block_details_smartspace("LLM_1_0_1") }}

## Example(s)

### Example 1: Simple response
- Create an `LLM` Block.
- Set `llm_config` (model name, temperature, pre-prompt).
- Provide a message: `"Summarize this document."`
- Output: `response` is a string (default schema is string).

### Example 2: Structured JSON response
- Define `response_schema` as an object, e.g. `{ "type": "object", "properties": { "summary": {"type":"string"} } }`.
- Provide a message; the block enforces structured output via tool-calling.
- Output: `response` is a JSON object; `sources` remains empty unless citing.

### Example 3: Use thread history for context
- Enable `use_thread_history=True`.
- Send multiple messages across steps; prior messages are included for context.

### Example 4: Citations with dataset items
- Provide `cited_documents` before calling `chat`.
- The block instructs the LLM to add citations like `(source_1)`, then resolves and normalizes them.
- Outputs: `response` (string or JSON) and `sources` (resolved dataset/file references).

### Example 5: Tool calling
- Add entries to `tools`; the LLM may trigger tool calls.
- After running a tool externally, resume via `handle_tool_result(tool_call_id, tool_result)`.

## Error Handling
- Empty tool call arguments or unexpected finish reasons raise errors.
- For string schema, pre-prompt discourages stringified JSON; for object schema, tool-based response wrapper enforces structure.
- Unresolved citations (e.g., `(source_X)`) are removed; only matched sources are emitted.

## FAQ

???+ question "What happens if the response schema is not provided?"

    It defaults to `{ "type": "string" }`. `response` will be a plain string unless you set an object schema.

???+ question "How does the Block handle structured responses?"

    With object schemas, a response function/tool is defined so the LLM returns schema-compliant JSON.

???+ question "Can I use the Block without thread history?"

    Yes. Set `use_thread_history=False` to only consider the current message.

???+ question "What happens if the LLM response type is a tool call?"

    Run the indicated tool(s) and pass results back via `handle_tool_result`. The block continues the conversation and emits final outputs when ready.
