{% set path = "assets/" + page.title + "-block.png" %}
{% if block_image_exists(path) %}
![{{page.title}}]({{path}}){{ block_image_sizing() }}
{% endif %}

## Overview
Retrieves all dataset items from every dataset in a specified dataspace. Useful for collecting all documents within a dataspace for analysis or downstream processing.

{{ generate_block_details_smartspace(page.title) }}

## Example(s)

### Example 1: Retrieve all documents from a dataspace
- Create a `GetAllDocuments` Block.
- Set `dataspace_id` to the target dataspace UUID.
- Output: list of `DataSetItem` objects aggregated from all datasets in the dataspace.

### Example 2: Use in a workflow to process documents
- Place `GetAllDocuments` upstream of an LLM or chunking step.
- Provide `dataspace_id`.
- Fan out the resulting `DataSetItem` list to downstream processors.

## Error Handling
- If `dataspace_id` is invalid or unavailable, the block raises an error from the configuration API call.
- If a dataspace has no datasets or no items, returns an empty list.

## FAQ

???+ question "What happens if the data space is empty?"

    If the specified data space contains no documents, the Block will return an empty list.

???+ question "Can I use this Block with different data spaces?"

    Yes, you can use this Block with any data space by setting the `dataspace_id` to the appropriate ID for the space you want to access.

???+ question "What is the output type?"

    A list of `DataSetItem` objects. Each item includes its `id`, `properties`, and metadata (dataset/container references, etc.).
