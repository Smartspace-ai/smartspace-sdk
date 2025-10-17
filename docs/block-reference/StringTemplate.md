{% set path = "assets/" + page.title + "-block.png" %}
{% if block_image_exists(path) %}
![{{page.title}}]({{path}}){{ block_image_sizing() }}
{% endif %}

## Overview
The `StringTemplate` Block generates formatted strings using Jinja2 templating with dynamic input values. Supports the full Jinja2 feature set including variable substitution, conditionals, loops, filters, and expressions. Ideal for constructing complex strings, formatted messages, code generation, and dynamic content creation.

{{ generate_block_details(page.title) }}

## Example(s)

### Example 1: Build a string with dynamic values
- Create a `StringTemplate` Block.
- Set the `template` to "Hello, {% raw %}{{name}}{% endraw %}!".
- Provide the input: `name="John"`.
- The Block will output: `"Hello, John!"`.

### Example 2: Use conditional logic in templates
- Set the `template` to "{% raw %}{% if age >= 18 %}Adult{% else %}Minor{% endif %}{% endraw %}"
- Provide inputs: `age=25`
- Output: `"Adult"`

### Example 3: Loop through a list
- Set the `template` to "Items: {% raw %}{% for item in items %}{{item}}{% if not loop.last %}, {% endif %}{% endfor %}{% endraw %}"
- Provide inputs: `items=["apple", "banana", "cherry"]`
- Output: `"Items: apple, banana, cherry"`

### Example 4: Use Jinja2 filters
- Set the `template` to "Hello, {% raw %}{{name|upper}}{% endraw %}! You have {% raw %}{{count|default(0)}}{% endraw %} messages."
- Provide inputs: `name="alice"`, `count=5`
- Output: `"Hello, ALICE! You have 5 messages."`

### Example 5: Format numbers and dates
- Set the `template` to "Price: ${% raw %}{{price|round(2)}}{% endraw %}, Date: {% raw %}{{date}}{% endraw %}"
- Provide inputs: `price=19.999`, `date="2024-10-15"`
- Output: `"Price: $20.0, Date: 2024-10-15"`

### Example 6: Nested variable access
- Set the `template` to "User: {% raw %}{{user.name}}{% endraw %}, Email: {% raw %}{{user.email}}{% endraw %}"
- Provide inputs: `user={"name": "John", "email": "john@example.com"}`
- Output: `"User: John, Email: john@example.com"`

## Error Handling
- If the template contains invalid Jinja2 syntax, the Block will raise a `TemplateSyntaxError`
- If a required variable is referenced but not provided, Jinja2 will raise an `UndefinedError`
- Use the `|default()` filter to provide fallback values for optional variables

## FAQ

???+ question "What happens if a required input is missing?"

    By default, Jinja2 will raise an `UndefinedError`. Use the `|default(value)` filter to provide fallback values: {% raw %}`{{name|default("Guest")}}`{% endraw %}.

???+ question "What Jinja2 features are supported?"

    All standard Jinja2 features:
    - Variable substitution: {% raw %}`{{variable}}`{% endraw %}
    - Conditionals: {% raw %}`{% if condition %}...{% endif %}`{% endraw %}
    - Loops: {% raw %}`{% for item in items %}...{% endfor %}`{% endraw %}
    - Filters: {% raw %}`{{value|filter_name}}`{% endraw %}
    - Expressions: {% raw %}`{{x + y}}`{% endraw %}, {% raw %}`{{items|length}}`{% endraw %}
    - Whitespace control, macros, and more

???+ question "How do I escape special characters?"

{% raw %}
    Use Jinja2's escaping:
    - Literal braces: use double curly braces (the standard Jinja variable delimiters)
    - Raw blocks: wrap content with `{ % raw % } ... { % endraw % }` (spaces added intentionally)
    - Escape variables: Use the `|escape` filter for HTML
{% endraw %}

???+ question "Can I use complex expressions?"

    Yes! Jinja2 supports arithmetic (`+`, `-`, `*`, `/`), comparisons (`==`, `!=`, `<`, `>`), logic (`and`, `or`, `not`), and more: {% raw %}`{{(price * 1.08)|round(2)}}`{% endraw %}

???+ question "How do I debug template issues?"

    Check the error message for line numbers and syntax issues. Common problems:
    - Missing closing tags: {% raw %}`{% if %}`{% endraw %} without {% raw %}`{% endif %}`{% endraw %}
    - Undefined variables: add `|default()` filters
    - Wrong variable types: ensure inputs match template expectations
