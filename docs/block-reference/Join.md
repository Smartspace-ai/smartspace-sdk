{% set path = "assets/" + page.title + "-block.png" %}
{% if block_image_exists(path) %}
![{{page.title}}]({{path}}){{ block_image_sizing() }}
{% endif %}

## Overview
The `Join` Block merges two lists of dictionaries based on a specified key, allowing SQL-like join operations (e.g., `INNER`, `LEFT`, `RIGHT`, `OUTER`). This Block is ideal for combining data from multiple sources by matching records on a common key, with flexible options for different types of joins.

{{ generate_block_details(page.title) }}

## Example(s)

### Example 1: Perform an INNER join
- Create a `Join` Block.
- Set `key` to `"id"` and `joinType` to `INNER`.
- Provide `left` and `right` lists of dictionaries where each dictionary contains an `"id"` key.
- The Block will output records with matching `"id"` values from both lists.

### Example 2: Perform a LEFT_OUTER join
- Set up a `Join` Block with `key` as `"user_id"` and `joinType` as `LEFT_OUTER`.
- Provide the `left` list as user data and the `right` list as order data, each containing `"user_id"`.
- The Block will output all user records, merging order data for users with matching `"user_id"`.

### Example 3: Perform an OUTER join
- Configure a `Join` Block with `key` set to `"product_id"` and `joinType` as `OUTER`.
- Supply `left` and `right` lists of product data with `"product_id"` as a shared key.
- The Block will output all records from both lists, merging where `"product_id"` matches.

## Error Handling
- If a record in either list lacks the specified key, the Block will raise a `KeyError`.
- If the `joinType` is invalid, a `ValueError` will be raised.

## FAQ

???+ question "What happens if a record doesn’t contain the specified key?"

    If a record in either the `left` or `right` list does not contain the specified join key, the Block will raise a `KeyError`, ensuring only records with the required key are processed.

???+ question "Can I specify custom join types?"

    Yes, the Block supports various join types, similar to SQL joins. Select the appropriate join type based on your requirements.

???+ question "How are fields merged from both lists?"

    Fields from both lists are merged into a single dictionary for each record in the output, based on the specified join type. If the same field exists in both records, the field from the `right` list will overwrite the one from the `left` list.

???+ question "Does this Block support joins on nested fields?"

    Currently, this Block only supports joins on top-level keys. For joins on nested fields, you would need to extract those fields into top-level keys before using this Block.
