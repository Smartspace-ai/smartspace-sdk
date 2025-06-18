{% set path = "assets/" + page.title + "-block.png" %}
{% if block_image_exists(path) %}
![{{page.title}}]({{path}}){{ block_image_sizing() }}
{% endif %}

## Overview
The `Join` Block performs advanced join operations between two lists of dictionaries based on a specified key. It merges the data according to the selected join type, similar to SQL join operations, allowing for flexible data integration and transformation. This Block is particularly useful for combining datasets from different sources while maintaining data relationships.

The Block supports multiple join types including `INNER`, `LEFT_INNER`, `LEFT_OUTER`, `RIGHT_INNER`, `RIGHT_OUTER`, and `OUTER`, providing complete control over how data is merged.

{{ generate_block_details(page.title) }}

## Example(s)

### Example 1: Inner join on user data
- Create a `Join` Block.
- Configure the key: `"id"` and join type: `INNER`.
- Provide left list: `[{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]`.
- Provide right list: `[{"id": 1, "age": 30}, {"id": 3, "age": 25}]`.
- The Block will output: `[{"id": 1, "name": "Alice", "age": 30}]` (only records with matching IDs).

### Example 2: Left outer join for complete user profiles  
- Set up a `Join` Block.
- Configure key: `"user_id"` and join type: `LEFT_OUTER`.
- Provide left list: `[{"user_id": 1, "name": "Alice"}, {"user_id": 2, "name": "Bob"}]`.
- Provide right list: `[{"user_id": 1, "department": "Engineering"}]`.
- The Block will output: `[{"user_id": 1, "name": "Alice", "department": "Engineering"}, {"user_id": 2, "name": "Bob"}]`.

### Example 3: Outer join to combine all data
- Create a `Join` Block.
- Configure key: `"product_id"` and join type: `OUTER`.
- Provide left list: `[{"product_id": "A", "name": "Widget"}]`.
- Provide right list: `[{"product_id": "A", "price": 10.99}, {"product_id": "B", "price": 5.99}]`.
- The Block will output: `[{"product_id": "A", "name": "Widget", "price": 10.99}, {"product_id": "B", "price": 5.99}]`.

### Example 4: Right inner join 
- Set up a `Join` Block.
- Configure key: `"category_id"` and join type: `RIGHT_INNER`.
- Provide left list: `[{"category_id": 1, "category_name": "Electronics"}]`.
- Provide right list: `[{"category_id": 1, "product": "Phone"}, {"category_id": 2, "product": "Book"}]`.
- The Block will output: `[{"category_id": 1, "category_name": "Electronics", "product": "Phone"}]`.

## Error Handling
- The `Join` Block requires that all records in both input lists contain the specified join key. If any record is missing the key, a `KeyError` will be raised.
- The Block validates the join type configuration and will raise a `ValueError` for invalid join types.
- If either input list is empty, the Block will return results according to the join type logic (e.g., empty result for INNER join, left data only for LEFT_OUTER).
- The Block handles duplicate keys by maintaining all records with the same key value in the join operation.

## FAQ

???+ question "What join types are supported?"

    The `Join` Block supports six join types: `INNER` (matching records only), `LEFT_INNER` (left records with matches), `LEFT_OUTER` (all left records), `RIGHT_INNER` (right records with matches), `RIGHT_OUTER` (all right records), and `OUTER` (all records from both sides).

???+ question "What happens when records have the same key but different field names?"

    The `Join` Block merges all fields from both records. If both records have the same field name, the right record's value will overwrite the left record's value in the merged result.

???+ question "Can I join on multiple keys simultaneously?"

    No, the current `Join` Block supports joining on a single key only. For multi-key joins, you might need to create a composite key field in your data before joining.

???+ question "How does the Block handle missing keys in records?"

    If any record in either input list is missing the specified join key, the Block will raise a `KeyError`. All records must contain the join key field.

???+ question "What happens with duplicate keys in the same list?"

    Records with duplicate keys are treated as separate entities. Each record with a matching key will be included in the join operation according to the selected join type.

???+ question "Can I join lists with different data types in the key field?"

    Yes, as long as the key values can be compared for equality. However, be cautious with mixed data types as they may not match as expected (e.g., string "1" vs integer 1).

???+ question "How does this compare to SQL joins?"

    The `Join` Block closely mirrors SQL join behavior. `INNER` works like SQL INNER JOIN, `LEFT_OUTER` like LEFT OUTER JOIN, `RIGHT_OUTER` like RIGHT OUTER JOIN, and `OUTER` like FULL OUTER JOIN. The `LEFT_INNER` and `RIGHT_INNER` types provide additional granular control.

???+ question "What's the performance impact of large datasets?"

    The Block creates dictionaries for efficient key lookups, so performance scales reasonably with data size. However, very large datasets may impact memory usage and processing time.

