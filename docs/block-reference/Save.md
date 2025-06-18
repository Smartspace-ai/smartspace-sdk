{% set path = "assets/" + page.title + "-block.png" %}
{% if block_image_exists(path) %}
![{{page.title}}]({{path}}){{ block_image_sizing() }}
{% endif %}

## Overview
The `Save` Block saves a single item with specified properties to the current dataset scope. It's designed for general-purpose data saving within dataset processing workflows. The block automatically handles ID generation if not provided and supports saving any properties as key-value pairs. This block operates within the dataset scope context, making it ideal for data processing pipelines.

{{ generate_block_details_smartspace(page.title) }}

## Example(s)

### Example 1: Save processed data
- Create a `Save` Block within a dataset scope.
- Provide properties: `title="Document Analysis"`, `status="completed"`, `score=0.95`.
- The Block will auto-generate an ID and save the item to the current dataset.

### Example 2: Save with custom ID
- Create a `Save` Block.
- Provide properties including ID: `id="12345678-1234-1234-1234-123456789abc"`, `name="Report"`, `type="PDF"`.
- The Block will use the provided ID and save/update the item.

### Example 3: Save analysis results
- Create a `Save` Block in a data processing flow.
- Provide results: `analysis_type="sentiment"`, `result="positive"`, `confidence=0.89`, `timestamp="2023-12-01"`.
- The Block saves the analysis results to the current dataset context.

### Example 4: Save with nested data
- Create a `Save` Block.
- Provide complex data: `name="Analysis"`, `metadata={"source": "file.txt", "processing": {"model": "v1.0", "time": 1.2}}`.
- The Block handles nested objects and arrays seamlessly.

## Error Handling
- If no dataset_id is available in the current scope, the Block will raise an exception.
- Invalid UUID formats in the `id` property will raise appropriate errors.
- The Block validates that it's operating within a proper dataset scope.

## FAQ

???+ question "What's the difference between Save, SaveChunk, and SaveToDataSet?"

    - **Save**: General-purpose saving within current dataset scope
    - **SaveChunk**: Specialized for chunk data, handles lists of chunks
    - **SaveToDataSet**: Saves to a specific dataset by ID (workspace block)
    
    Use Save for general data items within dataset processing flows.

???+ question "How does the dataset scope work?"

    The Save block operates within a dataset scope context. This means:
    - It must be used within a dataset processing flow
    - The dataset_id is provided by the surrounding context
    - No need to manually specify which dataset to save to

???+ question "How are IDs handled?"

    The Block looks for ID in properties using these keys (case-sensitive):
    - `id`
    - `ID`
    - `Id`
    
    If found, validates UUID format. If no ID provided, auto-generates a new UUID.

???+ question "What happens if I provide an existing ID?"

    The Block performs an "upsert" operation - if an item with the given ID exists, it updates it; otherwise, it creates a new item.

???+ question "Can I save any type of data?"

    Yes, the Block supports any JSON-serializable properties including strings, numbers, booleans, arrays, nested objects, and null values.