{% set path = "assets/" + page.title + "-block.png" %}
{% if block_image_exists(path) %}
![{{page.title}}]({{path}}){{ block_image_sizing() }}
{% endif %}

## Overview
The `StringConst` Block outputs a predefined string value that is configured when the Block is set up. This Block is useful for providing static text, messages, file paths, URLs, or any constant string values in your workflows. The string value is specified in the Block's configuration and remains constant throughout execution.

{{ generate_block_details(page.title) }}

## Example(s)

### Example 1: Output a simple text constant
- Create a `StringConst` Block.
- Configure the output value: `"Hello, World!"`.
- The Block will output: `"Hello, World!"`.

### Example 2: Provide a file path
- Set up a `StringConst` Block.
- Configure the value: `"/home/user/documents/data.csv"`.
- The Block will output the file path string for use by other Blocks.

### Example 3: Supply a URL endpoint
- Create a `StringConst` Block.
- Configure the value: `"https://api.example.com/v1/users"`.
- The Block will output this URL string for HTTP requests or API calls.

### Example 4: Use multi-line text
- Set up a `StringConst` Block.
- Configure with multi-line text: `"Line 1\nLine 2\nLine 3"`.
- The Block will output the multi-line string preserving line breaks.

### Example 5: Handle empty string
- Create a `StringConst` Block.
- Configure with an empty string: `""`.
- The Block will output an empty string `""`.

### Example 6: Include special characters
- Set up a `StringConst` Block.
- Configure the value: `"User: admin@domain.com | Status: 'active'"`.
- The Block will output the string with special characters and quotes.

## Error Handling
- The `StringConst` Block has minimal error handling requirements since it outputs a pre-configured static value.
- The Block accepts any valid string input during configuration, including empty strings and strings with special characters.
- The Block will always output the exact string value that was configured, preserving formatting and special characters.
- Very long strings are supported within system memory limits.

## FAQ

???+ question "Can I modify the string value after the Block is configured?"

    No, the `StringConst` Block outputs a constant string that is set during configuration. If you need dynamic string values, consider using template blocks like `StringTemplate` or `TemplatedObject`.

???+ question "How do I include line breaks and special characters?"

    You can include line breaks using `\n`, tabs with `\t`, and other escape sequences. Special characters like quotes can be included directly or escaped as needed.

???+ question "Can I use this Block for template strings?"

    `StringConst` outputs static strings only. For dynamic string generation with variables, use the `StringTemplate` block which supports Jinja2 templating.

???+ question "What's the maximum length of string I can configure?"

    There's no practical limit imposed by the Block itself. The limitation would be system memory. However, very large strings may impact performance.

???+ question "How does this differ from other constant Blocks?"

    `StringConst` specifically outputs string text, while `IntegerConst` outputs numbers and `DictConst` outputs objects. Use `StringConst` for text data, messages, paths, URLs, and any textual content.

???+ question "Can I include JSON or XML content in the string?"

    Yes, you can configure `StringConst` with any text content including JSON, XML, or other structured text formats. The content will be treated as a plain string.

???+ question "Does the Block support Unicode and international characters?"

    Yes, `StringConst` fully supports Unicode characters, allowing you to configure strings in any language or with special symbols.

