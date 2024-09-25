{% set path = "assets/" + page.title + "-block.png" %}
{% if block_image_exists(path) %}
![{{page.title}}]({{path}}){{ block_image_sizing() }}
{% endif %}

## Overview
The `GetAllDocuments` Block retrieves all documents from a specified data space using a `SearchService`. This Block is useful when you need to gather and process a collection of documents stored in a data space for analysis or further operations.

{{ generate_block_details_smartspace(page.title) }}

## Example(s)

### Example 1: Retrieve all documents from a data space
- Create a `GetAllDocuments` Block.
- Set the `dataspace_id` to the ID of the data space you want to retrieve documents from.
- The Block will return a list of documents, each containing the document path and content.

### Example 2: Use in a workflow to process documents
- Set up a `GetAllDocuments` Block in a workflow.
- Provide the `dataspace_id` to specify the data space.
- After retrieving the documents, pass them to another block for processing, such as content analysis or text summarization.

## Error Handling
- If the `dataspace_id` is invalid or the data space cannot be accessed, the Block will raise an error.
- If no documents are found in the data space, the Block will return an empty list.

## FAQ

???+ question "What happens if the data space is empty?"

    If the specified data space contains no documents, the Block will return an empty list.

???+ question "Can I use this Block with different data spaces?"

    Yes, you can use this Block with any data space by setting the `dataspace_id` to the appropriate ID for the space you want to access.

???+ question "How are the documents formatted in the output?"

    The Block outputs a list of `GetAllDocumentsResult` objects, each containing the `path` (the document's location) and `content` (the text of the document).