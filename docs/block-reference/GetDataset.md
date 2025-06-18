{% set path = "assets/" + page.title + "-block.png" %}
{% if block_image_exists(path) %}
![{{page.title}}]({{path}}){{ block_image_sizing() }}
{% endif %}

## Overview
The `GetDataSet` Block retrieves dataset items with advanced SQL-style filtering and sorting capabilities. It provides comprehensive data retrieval features including SQL-style property filtering with full operator support, complex logical expressions, multi-datatype support, flexible pagination, and SQL-style sorting with multiple columns and directions. The block converts SQL-style filter and sort expressions directly to Cosmos DB queries for optimal performance.

{{ generate_block_details_smartspace(page.title) }}

## Example(s)

### Example 1: Retrieve all items from a dataset
- Create a `GetDataSet` Block.
- Set `dataset_id` to your target dataset's UUID.
- Leave other parameters at defaults.
- The Block will return the first 50 items from the dataset.

### Example 2: Filter items by status and date
- Create a `GetDataSet` Block.
- Set `dataset_id` to your dataset's UUID.
- Set `filter` to `"Status = 'Published' AND createdAt >= '2023-01-01'"`.
- The Block will return only published items created after January 1, 2023.

### Example 3: Complex filtering with sorting
- Create a `GetDataSet` Block.
- Set `filter` to `"(Type IN ['Document', 'Report'] OR Category = 'Analysis') AND Size > 1000"`.
- Set `sort` to `"Size DESC, CreatedAt ASC"`.
- Set `take` to `25`.
- The Block will return matching items sorted by size (largest first), then by creation date.

### Example 4: Paginated retrieval
- Create a `GetDataSet` Block.
- Set `skip` to `20`.
- Set `take` to `10`.
- Set `sort` to `"Name ASC"`.
- The Block will return items 21-30 when sorted alphabetically by name.

## Error Handling
- If the Block is used outside of a workspace context, it will raise an exception.
- If no dataset_id is provided or the dataset is not found in the workspace, it returns an empty list.
- Invalid SQL syntax in filter or sort expressions will raise appropriate parsing errors.

## FAQ

???+ question "What SQL operators are supported in filters?"

    The Block supports:
    - **Comparison**: `=`, `!=`, `<>`, `>`, `>=`, `<`, `<=`
    - **IN operator**: `Type IN ['Document', 'Image', 'Video']`
    - **NULL checks**: `Description = null`, `Tags != null`
    - **Logical**: `AND`, `OR`, with parentheses for grouping

???+ question "What data types can I use in filters?"

    - **Strings**: Must be quoted - `Name = 'example.pdf'`
    - **Numbers**: Direct values - `Size = 1000`, `Rating = 4.5`
    - **Booleans**: `IsPublic = true`, `IsActive = false`
    - **Dates**: ISO format - `createdAt >= '2023-01-01T00:00:00Z'`
    - **NULL**: `Description = null`

???+ question "How does sorting work?"

    Sorting supports:
    - Single column: `'CreatedAt ASC'` or `'Name DESC'`
    - Multiple columns: `'CreatedAt DESC, Name ASC'`
    - Custom properties from your dataset
    - Standard properties like `createdAt` and `modifiedAt`

???+ question "What's the difference between GetDataSet and SearchDataSet?"

    - **GetDataSet**: Retrieves items based on exact property matches and conditions
    - **SearchDataSet**: Performs semantic/full-text search across content, then applies filters

???+ question "Can I retrieve from multiple datasets?"

    No, the Block retrieves from a single dataset specified by `dataset_id`. To retrieve from multiple datasets, you would need to use multiple GetDataSet blocks or implement custom logic.