{% set path = "assets/" + page.title + "-block.png" %}
{% if block_image_exists(path) %}
![{{page.title}}]({{path}}){{ block_image_sizing() }}
{% endif %}

## Overview
The `TemplatedObject` Block takes a Jinja2 template string and dynamically generates JSON objects by filling the template with provided input values. This Block is powerful for creating structured data objects, API payloads, configuration files, or any JSON structure that needs to be dynamically populated based on runtime values.

The Block uses Jinja2 templating syntax, allowing for complex logic including conditionals, loops, and filters. After rendering the template, it automatically parses the result into a JSON object, ensuring the output is properly structured data rather than a string.

{{ generate_block_details(page.title) }}

## Example(s)

### Example 1: Create a user profile object
- Create a `TemplatedObject` Block.
- Configure template: `{"name": "{{name}}", "age": {{age}}, "active": {{active}}}`.
- Provide inputs: `name="Alice"`, `age=30`, `active=true`.
- The Block will output: `{"name": "Alice", "age": 30, "active": true}`.

### Example 2: Generate API request payload
- Set up a `TemplatedObject` Block.
- Configure template: `{"query": "{{search_term}}", "filters": {"category": "{{category}}", "min_price": {{min_price}}}, "limit": {{limit}}}`.
- Provide inputs: `search_term="laptop"`, `category="electronics"`, `min_price=500`, `limit=10`.
- The Block will output a structured API request object.

### Example 3: Use conditional logic in template
- Create a `TemplatedObject` Block.
- Configure template: `{"user": "{{username}}", "role": "{{role}}"{% if is_admin %}, "permissions": ["read", "write", "admin"]{% else %}, "permissions": ["read"]{% endif %}}`.
- Provide inputs: `username="john"`, `role="user"`, `is_admin=false`.
- The Block will output: `{"user": "john", "role": "user", "permissions": ["read"]}`.

### Example 4: Generate array with loop
- Set up a `TemplatedObject` Block.
- Configure template: `{"items": [{% for item in items %}"{{item}}"{% if not loop.last %},{% endif %}{% endfor %}], "count": {{items|length}}}`.
- Provide inputs: `items=["apple", "banana", "cherry"]`.
- The Block will output: `{"items": ["apple", "banana", "cherry"], "count": 3}`.

### Example 5: Handle nested objects
- Create a `TemplatedObject` Block.
- Configure template: `{"person": {"name": "{{name}}", "contact": {"email": "{{email}}", "phone": "{{phone}}"}}, "metadata": {"created": "{{timestamp}}", "source": "{{source}}"}}`.
- Provide inputs with nested structure for a complex JSON object.

## Error Handling
- If the Jinja2 template contains syntax errors, the Block will raise a `TemplateError` with details about the template issue.
- If the rendered template does not produce valid JSON, the Block will raise a `JSONDecodeError` indicating the parsing failure.
- Missing input variables referenced in the template will cause Jinja2 to raise an `UndefinedError`.
- The Block handles type conversion automatically, ensuring strings are properly quoted in the JSON output while numbers and booleans are not quoted.
- Template rendering errors are caught and re-raised as `ValueError` with descriptive error messages.

## FAQ

???+ question "What Jinja2 features are supported?"

    The `TemplatedObject` Block supports all standard Jinja2 features including variables, filters, conditionals (`{% if %}`), loops (`{% for %}`), macros, and custom filters. You have access to the full Jinja2 templating syntax.

???+ question "How are different data types handled in the template?"

    The Block automatically handles type formatting: strings are quoted, numbers and booleans are not quoted, and complex objects are JSON-serialized. For example, a string input "hello" becomes `"hello"` in JSON, while a number 42 remains `42`.

???+ question "Can I include arrays and nested objects in my template?"

    Yes, you can create complex nested structures including arrays, objects, and mixed data types. Use Jinja2 loops for dynamic arrays and nested template syntax for complex object structures.

???+ question "What happens if my template produces invalid JSON?"

    If the rendered template is not valid JSON (e.g., missing quotes, trailing commas, invalid syntax), the Block will raise a `JSONDecodeError` with details about the parsing failure.

???+ question "Can I use conditional logic to include or exclude fields?"

    Yes, use Jinja2 conditional statements (`{% if condition %}`) to dynamically include or exclude fields based on input values. This is useful for creating objects with optional fields.

???+ question "How do I handle lists and arrays in the template?"

    Use Jinja2 loops (`{% for item in items %}`) to iterate over input lists. Be careful with JSON syntax, ensuring proper comma placement and array brackets.

???+ question "Can I apply filters to transform input values?"

    Yes, Jinja2 filters are fully supported. You can use built-in filters like `|upper`, `|length`, `|default()`, or create custom transformations within the template.

???+ question "What's the difference between this and StringTemplate?"

    `TemplatedObject` specifically generates and parses JSON objects, ensuring the output is structured data. `StringTemplate` generates plain text strings. Use `TemplatedObject` when you need structured data objects.

???+ question "Can I preview the rendered template before JSON parsing?"

    The Block automatically renders and parses in one step. If you need to debug template issues, ensure your template syntax is correct and that all referenced variables are provided as inputs.

