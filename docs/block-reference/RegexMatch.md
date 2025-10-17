{% set path = "assets/" + page.title + "-block.png" %}
{% if block_image_exists(path) %}
![{{page.title}}]({{path}}){{ block_image_sizing() }}
{% endif %}

## Overview
The `RegexMatch` Block performs regex-based pattern matching and replacement on string input. It operates in two modes: **match mode** (when `replace_with` is empty) returns a list of all pattern matches, while **replace mode** (when `replace_with` is provided) performs find-and-replace operations. Supports full Python regex syntax including capture groups, lookaheads, and backreferences.

This Block is useful for extracting data based on specific patterns (emails, phone numbers, etc.) or transforming text through pattern-based substitutions.

{{ generate_block_details(page.title) }}

## Example(s)

### Example 1: Find all numbers in a string
- Create a `RegexMatch` Block.
- Set the `regex` to `\d+` (this regex matches one or more digits).
- Provide the input string: `"My phone number is 12345 and my zip code is 67890."`
- The Block will output: `["12345", "67890"]`.

### Example 2: Match words starting with a specific letter
- Set up a `RegexMatch` Block.
- Set the `regex` to `\b[Aa]\w*` (this regex matches words starting with "A" or "a").
- Provide the input string: `"Alice and Bob are attending the event."`
- The Block will output: `["Alice", "and", "are"]`.

### Example 3: Replace all occurrences of a pattern
- Create a `RegexMatch` Block.
- Set the `regex` to `\d+` (matches digits).
- Set `replace_with` to `"***"`.
- Provide the input string: `"My phone is 12345 and zip is 67890."`
- The Block will output: `"My phone is *** and zip is ***."`

### Example 4: Use capture groups for advanced replacement
- Create a `RegexMatch` Block.
- Set the `regex` to `(\w+)@(\w+\.com)` (captures email parts).
- Set `replace_with` to `"user: \1, domain: \2"`.
- Provide input: `"Contact: john@example.com"`
- Output: `"Contact: user: john, domain: example.com"`

### Example 5: No matches found
- Create a `RegexMatch` Block.
- Set the `regex` to `\d+` (this regex matches digits).
- Provide the input string: `"No numbers here."`
- The Block will output: `["No match found"]` as there are no digits in the string.

### Example 6: Handle regex errors
- Create a `RegexMatch` Block.
- Set an invalid regex, such as `\d++`.
- The Block will return an error message like `["Error: nothing to repeat at position 3"]`.

## Error Handling
- If the regex pattern is invalid, the Block will return a list containing an error message with the exception details.
- If no matches are found, the Block will return `["No match found"]`.

## FAQ

???+ question "What happens if the regex pattern is invalid?"
    
    If the provided regex pattern is invalid, the Block will catch the exception and return a list containing the error message. This allows you to handle regex-related errors gracefully.

???+ question "Can I use this Block for complex regex patterns?"
    
    Yes, the `RegexMatch` Block supports any valid regex pattern, allowing you to handle complex string matching tasks such as extracting specific formats or patterns from text.

???+ question "What if the input string contains no matches?"
    
    If the input string does not match the provided regex pattern, the Block will return `["No match found"]`.

???+ question "Does this Block support multiline input?"
    
    Yes, the Block can handle multiline input, but you'll need to adjust the regex pattern accordingly (e.g., use `re.MULTILINE` flags or include newline characters in the regex if needed).

???+ question "How do I choose between match mode and replace mode?"

    - **Match mode** (default): Leave `replace_with` empty. Returns `list[str]` of all matches.
    - **Replace mode**: Provide `replace_with` string. Returns modified `str` with all matches replaced.

???+ question "Can I use backreferences in replacements?"

    Yes! Use `\1`, `\2`, etc. in `replace_with` to reference capture groups from your regex pattern.

???+ question "What regex features are supported?"

    Full Python `re` module syntax: capture groups `()`, alternation `|`, quantifiers `*+?{}`, character classes `[]`, anchors `^$`, lookaheads/lookbehinds, named groups, and more.