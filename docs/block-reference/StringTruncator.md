{% set path = "assets/" + page.title + "-block.png" %}
{% if block_image_exists(path) %}
![{{page.title}}]({{path}}){{ block_image_sizing() }}
{% endif %}

## Overview
The `StringTruncator` Block truncates a string input based on a specified token limit. This Block is useful when you need to limit the length of a string to a certain number of tokens, particularly in contexts where token usage is important, such as working with language models like GPT-3.5. The Block utilizes a tokenizer specific to the selected model to ensure accurate token counting and truncation.

The default token limit is `100` tokens, and the default model for tokenization is `gpt-3.5-turbo`, but both can be configured.

{{ generate_block_details(page.title) }}

## Example(s)

### Example 1: Truncate a string with the default token limit
- Create a `StringTruncator` Block.
- Set the `max_token` to `100`.
- Provide the input string: `"This is a long text that needs to be truncated based on the token limit."`
- If the input exceeds 100 tokens, the Block will return a truncated version of the string. If it is shorter, the original string will be returned.

### Example 2: Truncate a string with a custom token limit
- Set up a `StringTruncator` Block.
- Set the `max_token` to `50`.
- Provide the input string: `"This is an even longer text that may need to be truncated based on a smaller token limit."`
- The Block will truncate the string at the 50-token mark and return the truncated result.

### Example 3: Handle a short string under the token limit
- Create a `StringTruncator` Block.
- Set the `max_token` to `100`.
- Provide a short input string: `"This is a short string."`
- The Block will return the original string, as it is under the token limit.

## Error Handling
- If the model name is invalid or unsupported, the Block will raise a `RuntimeError` indicating that the tokenizer could not be loaded.
- If an issue occurs during tokenization or truncation, the Block will raise a `RuntimeError` describing the problem.

## FAQ

???+ question "What happens if the input string is shorter than the token limit?"
    
    If the input string contains fewer tokens than the specified token limit, the Block will return the original string without truncation.

???+ question "Can I use a custom model for tokenization?"
    
    Yes, you can specify a custom model for tokenization by setting the `model_name` parameter. The Block will use the tokenizer associated with the model to accurately truncate the string based on the token limit.

???+ question "What happens if the token limit is set too high?"
    
    If the token limit is higher than the number of tokens in the input string, the Block will simply return the original string. The token limit acts as an upper bound, not a minimum requirement.

???+ question "Does this Block handle multi-byte characters?"
    
    Yes, the Block accounts for multi-byte characters through the tokenizer, ensuring that token counting and truncation are handled correctly for any type of text input, including those with multi-byte characters like emojis or non-Latin scripts.