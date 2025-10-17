{% set path = "assets/" + page.title + "-block.png" %}
{% if block_image_exists(path) %}
![{{page.title}}]({{path}}){{ block_image_sizing() }}
{% endif %}

## Overview

!!! warning "Deprecated Block"
    **This block is deprecated and will be removed in a future version.** Use the `LLM` block instead, which now includes built-in tool calling capabilities with better performance and features.

The `LLMWithTools` Block allows interaction with a Language Learning Model (LLM) and integrates additional tools to assist the LLM in generating more complex responses. This Block supports multiple tools, which can be invoked by the LLM when needed. It manages both the LLM's responses and the results from tool invocations.

This Block is useful when you want the LLM to dynamically call different tools based on user inputs, allowing for more versatile and context-aware conversations.

{{ generate_block_details_smartspace(page.title) }}

## Example(s)

### Example 1: Use the LLM to select a tool
- Create an `LLMWithTools` Block.
- Define tools like `"Tool1"` and `"Tool2"` that the LLM can choose from.
- Provide an input message: `"Which tool should I use for this task?"`
- The Block will invoke the appropriate tool based on the LLM’s decision, process the result, and return a response.

### Example 2: Handling a response without tool invocation
- Set up an `LLMWithTools` Block with tools defined.
- Provide a message where no tool invocation is necessary: `"Summarize the document."`
- The LLM will generate the response directly and send it back without calling any tools.

### Example 3: Multiple tool calls in a single interaction
- Set up an `LLMWithTools` Block.
- The LLM can call multiple tools during the interaction, processing each tool’s output and using the results to generate a final response.

### Example 4: Resume after external tool execution
- When a tool requires external execution, capture the tool call ID and run the tool outside the block.
- Feed the tool result back into your flow (e.g., via a follow-up step), then re‑invoke the block’s resume logic (for the modern replacement `LLM`, this is `handle_tool_result(tool_call_id, tool_result)`).
- The conversation continues and the model produces a final response with incorporated tool results.

### Example 5: Tool naming edge cases
- If your tool names contain spaces or punctuation, the successor `LLM` block sanitizes names internally (spaces removed). Prefer simple, alphanumeric names to avoid ambiguity.
- In older `LLMWithTools` flows, keep names short and unique to reduce LLM confusion.

## Error Handling
- If tool results are not available, the Block will raise an error.
- If the LLM response type is unexpected, the Block will attempt to handle the error gracefully by sending back a default response.
 - For complex interactions, verify tool outputs are JSON-serializable (or string) and keep payload sizes reasonable to avoid token budget issues.

## FAQ

???+ question "How does the Block handle tool invocations?"

    The LLM can call tools defined in the `tools` dictionary. The Block waits for the tool's results, appends the result to the conversation history, and allows the LLM to continue processing the message.

???+ question "Can I define custom tools for the LLM to use?"

    Yes, you can define custom tools in the `tools` dictionary. Each tool has its own functionality and can be invoked by the LLM during conversation based on the input message.

???+ question "What happens if the LLM doesn’t need a tool?"

    If the LLM determines that no tools are necessary for a particular response, it will generate the response directly and return it without invoking any tools.

???+ question "Can the Block handle multiple tool calls in a single interaction?"

    Yes, the Block is capable of handling multiple tool calls in a single interaction. It manages tool call results and appends them to the conversation history, ensuring that the LLM can utilize multiple tools as needed.

???+ question "Should I migrate existing flows?"

    Yes. `LLMWithTools` is deprecated. The modern `LLM` block offers built‑in tool calling, better schema enforcement, citation handling, and improved error control. Migrate when practical.
