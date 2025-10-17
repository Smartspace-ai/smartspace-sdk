{% set path = "assets/" + page.title + "-block.png" %}
{% if block_image_exists(path) %}
![{{page.title}}]({{path}}){{ block_image_sizing() }}
{% endif %}

## Overview
Fill a DOCX template with structured data and output a new document. Retrieves a DOCX template from blob storage, renders it with Jinja2 using your input data, and uploads the filled document back to storage.

## Description

Fills a DOCX template with provided data and saves the filled document to blob storage.

Notes:
- Uses `docxtpl` for templating; template variables correspond to keys in the provided data object
- `output_file_name` controls the base filename (without extension)
- `template_file` must be a valid DOCX file stored in blob storage

{{ generate_block_details_smartspace(page.title) }}



## Example(s)

### Example 1: Simple field replacement
- Config: `output_file_name="Invoice_2024"`, `template_file=<File id=... name="invoice_template.docx">`
- Input `data`:
  `{ "invoice_number": "INV-1001", "customer": {"name": "Acme"}, "total": 199.0 }`
- Output: File `Invoice_2024.docx` with placeholders replaced.

### Example 2: With loops and conditionals
- Template uses `docxtpl` Jinja: iterate over `items` and conditionally show a note.
- Input `data` includes `items=[{"name":"Widget","price":10.0}]`.
- Output: Populated table and conditional sections rendered.

## Error Handling
- Missing or unreadable template file raises a descriptive error.
- Invalid template syntax or missing variables during render raises a `docxtpl` error (surfaced as an exception with details and a traceback context).
- If the filled document cannot be uploaded to blob storage, the block raises an error.

## FAQ

???+ question "What template syntax is supported?"

    Standard `docxtpl` Jinja syntax: variables, loops, conditionals, filters. Use `{% raw %}`{{ var }}`{% endraw %}`, `{% raw %}`{% for item in items %}`{% endraw %}`, `{% raw %}`{% if condition %}`{% endraw %}`.

???+ question "Can I pass nested objects?"

    Yes. Nested dicts are supported, e.g., `{% raw %}`{{ customer.name }}`{% endraw %}` or within loops.

???+ question "How is the output file named?"

    The created file uses `output_file_name` with `.docx` appended.
