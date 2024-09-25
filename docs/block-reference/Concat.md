{% set path = "assets/" + page.title + "-block.png" %}
{% if block_image_exists(path) %}
![{{page.title}}]({{path}}){{ block_image_sizing() }}
{% endif %}

## Overview
The `Concat` Block concatenates two sequences, which can either be lists or strings. This Block takes two input sequences and returns the result of appending the second sequence to the first. It supports both string and list types, making it useful for combining different kinds of data.

{{ generate_block_details(page.title) }}

## Example(s)

### Example 1: Concatenate two strings
- Create a `Concat` Block.
- Provide the input strings: `"Hello, "` and `"World!"`.
- The Block will output: `"Hello, World!"`, concatenating the two strings.

### Example 2: Concatenate two lists
- Set up a `Concat` Block.
- Provide the input lists: `[1, 2, 3]` and `[4, 5, 6]`.
- The Block will output: `[1, 2, 3, 4, 5, 6]`, merging the two lists into one.

### Example 3: Handle empty inputs
- Create a `Concat` Block.
- Provide an empty list and a non-empty list: `[]` and `[1, 2, 3]`.
- The Block will output: `[1, 2, 3]`, as the empty list does not affect the result.

## Error Handling
- The `Concat` Block expects both inputs to be of the same type (either both lists or both strings). If the types do not match (e.g., concatenating a string with a list), the Block will raise a `TypeError`.
- If the inputs are neither lists nor strings, the Block may raise an error or behave unexpectedly.

## FAQ

???+ question "What happens if one of the inputs is empty?"
    
    If one of the inputs is an empty list or string, the Block will simply return the non-empty input as the result. For example, concatenating `"Hello, "` with an empty string will return `"Hello, "`.

???+ question "Can I concatenate different types, like a string and a list?"
    
    No, the `Concat` Block requires both inputs to be of the same type. Attempting to concatenate a string and a list will result in a `TypeError`. Ensure that both inputs are either lists or strings.

???+ question "Does this Block work with other sequence types like tuples?"
    
    No, the `Concat` Block is designed to work specifically with strings and lists. Other sequence types like tuples are not supported.

???+ question "What happens if I concatenate very large lists or strings?"
    
    The `Concat` Block will handle large inputs, but performance may degrade with very large lists or strings depending on available memory and system resources.