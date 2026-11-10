{% set path = "assets/" + page.title + "-block.png" %}
{% if block_image_exists(path) %}
![{{page.title}}]({{path}}){{ block_image_sizing() }}
{% endif %}

## Overview
The `TypeSwitch` Block allows you to route inputs to different outputs based on their data type or schema. This Block evaluates the input against a list of predefined schema options and sends the input to the first matching output. It's particularly useful for handling heterogeneous data streams where different data types need to be processed through different pathways.

The Block uses strict schema validation to determine type matches, ensuring that only inputs that exactly conform to a schema are routed to the corresponding output.

{{ generate_block_details(page.title) }}

## Example(s)

### Example 1: Route strings and numbers to different outputs
- Create a `TypeSwitch` Block.
- Configure two options: one with a string schema routing to a "text_output", and another with a number schema routing to a "number_output".
- Provide the input `"Hello World"` (string).
- The Block will validate the input against the string schema first, match it, and send `"Hello World"` to the "text_output".

### Example 2: Handle complex object routing
- Set up a `TypeSwitch` Block.
- Define options for different object schemas: one for user objects `{"name": str, "age": int}` and another for product objects `{"id": int, "price": float}`.
- Provide the input `{"name": "Alice", "age": 30}`.
- The Block will match this against the user schema and route it to the corresponding user processing output.

### Example 3: First-match routing behavior
- Create a `TypeSwitch` Block.
- Configure multiple options where some schemas might overlap (e.g., both accepting integers).
- Provide an integer input like `42`.
- The Block will send the input to the first option that matches, demonstrating the first-match routing behavior.

### Example 4: Handle lists with different element types
- Set up a `TypeSwitch` Block.
- Define options for `list[str]` routing to a "string_list_output" and `list[int]` routing to a "number_list_output".
- Provide the input `["apple", "banana", "cherry"]`.
- The Block will match this as a list of strings and route it to the "string_list_output".

## Error Handling
- If the input does not match any of the defined schemas, the Block will not send the input to any output, effectively filtering out unmatched inputs.
- The Block uses strict validation, meaning inputs must exactly conform to the schema requirements. Partial matches or type coercions will not occur.
- If there are issues with the schema definitions themselves, the Block may raise validation errors during setup.
- The Block processes options in the order they are provided, so schema order matters when there might be overlapping type matches.

## FAQ

???+ question "What happens if the input does not match any schema?"

    The Block will skip the input, and no outputs will be triggered. This allows the Block to act as a filter, only passing through inputs that match predefined schemas.

???+ question "Can I have multiple schemas that might match the same input?"
    
    Yes, but the Block will only route the input to the first matching schema option. If you have overlapping schemas, ensure they are ordered from most specific to least specific to get the desired routing behavior.

???+ question "Does the Block support nested object validation?"
    
    Yes, the Block uses Pydantic model validation, which supports complex nested schemas including objects, lists, and deeply nested structures. You can define schemas for complex data structures and the Block will validate them accordingly.

???+ question "What types of schemas can I use with TypeSwitch?"
    
    You can use any schema that Pydantic supports, including primitive types (str, int, float, bool), collections (list, dict), and complex custom models. The schema system is very flexible and supports validation rules, optional fields, and type constraints.

???+ question "Can I use TypeSwitch to filter out invalid data?"
    
    Yes, TypeSwitch is excellent for data filtering. Any input that doesn't match your defined schemas will be discarded, allowing only valid, well-structured data to proceed through your pipeline.

???+ question "How does strict validation work?"
    
    Strict validation means that inputs must exactly match the schema without any type coercion. For example, if your schema expects an integer, a string like "123" will not be automatically converted to an integer - it will fail validation and not be routed.

???+ question "Can I modify the order of schema checking?"
    
    Yes, the order of options in your TypeSwitch configuration determines the order of schema checking. The Block will check schemas in the order you provide them and route to the first match found.

???+ question "What happens with very large or complex inputs?"
    
    The Block will handle large and complex inputs as long as they can be validated by Pydantic. However, very complex validation might impact performance. Consider the complexity of your schemas when designing your data routing logic.