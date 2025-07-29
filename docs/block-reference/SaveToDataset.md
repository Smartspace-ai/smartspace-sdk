{% set path = "assets/" + page.title + "-block.png" %}
{% if block_image_exists(path) %}
![{{page.title}}]({{path}}){{ block_image_sizing() }}
{% endif %}

## Overview
The `SaveToDataSet` Block saves a single item with specified properties to a specific dataset identified by ID. It allows you to upsert (insert or update) data items into a dataset within your workspace. The block automatically handles ID generation if not provided and supports saving any properties as key-value pairs.

{{ generate_block_details_smartspace(page.title) }}

## Example(s)

### Example 1: Save a simple item to a dataset
- Create a `SaveToDataSet` Block.
- Set `dataset_id` to your target dataset's UUID.
- Provide properties: `name="Document1"`, `type="PDF"`, `size=1024`.
- The Block will save the item with these properties and auto-generate an ID.

### Example 2: Save an item with a specific ID
- Create a `SaveToDataSet` Block.
- Set `dataset_id` to your dataset's UUID.
- Provide properties: `id="123e4567-e89b-12d3-a456-426614174000"`, `title="Report"`, `status="Published"`.
- The Block will save or update the item with the specified ID.

### Example 3: Update an existing item
- Create a `SaveToDataSet` Block.
- Set `dataset_id` to your dataset's UUID.
- Provide properties including an existing `id`.
- The Block will update the existing item with the new properties.

### Example 4: Save complex nested data
- Create a `SaveToDataSet` Block.
- Set `dataset_id` to your dataset's UUID.
- Provide properties: `name="Analysis"`, `metadata={"author": "John", "tags": ["finance", "Q4"]}`, `results=[1, 2, 3]`.
- The Block will save the item with nested objects and arrays.

## Error Handling
- If no `dataset_id` is provided, the Block will raise an exception.
- If an invalid UUID format is provided in the `id` property, an exception will be raised.
- The Block will raise an error if it cannot save to the specified dataset.

## FAQ

???+ question "How does the Block handle IDs?"

    The Block looks for an ID in the properties using these keys (case-sensitive):
    - `id`
    - `ID` 
    - `Id`
    
    If found, it validates the UUID format. If no ID is provided, it auto-generates a new UUID.

???+ question "What's the difference between Save, SaveChunk, and SaveToDataSet?"

    - **Save**: Saves to the current dataset scope (requires dataset context)
    - **SaveChunk**: Saves one or more chunk items to the current dataset scope
    - **SaveToDataSet**: Saves to a specific dataset by ID (workspace block)

???+ question "What property types are supported?"

    The Block supports any JSON-serializable properties including:
    - Strings, numbers, booleans
    - Arrays/lists
    - Nested objects/dictionaries
    - Null values
    - Date strings (stored as strings)

???+ question "Does this perform an insert or update?"

    The Block performs an "upsert" operation - if an item with the given ID exists, it updates it; otherwise, it creates a new item.

???+ question "Can I save multiple items at once?"

    No, this Block saves one item at a time. To save multiple items, you would need to:
    - Use the Block in a loop
    - Use the SaveChunk block for chunk data
    - Create a custom solution for batch operations