{% set path = "assets/" + page.title + "-block.png" %}
{% if block_image_exists(path) %}
![{{page.title}}]({{path}}){{ block_image_sizing() }}
{% endif %}

## Overview
The `SQL` Block executes asynchronous SQL queries on a database using SQLAlchemy. This Block supports all SQL query types, including `SELECT`, `INSERT`, `UPDATE`, and `DELETE`. For data-modifying queries (such as `INSERT`, `UPDATE`, and `DELETE`), the transaction is automatically committed. If the initial database connection fails (e.g., due to the database being unavailable), the Block will attempt one reconnection before raising an error.

This Block is useful for applications that need to interact with relational databases, allowing for flexible querying and data manipulation using SQL.

**Key Features**:

- Supports a wide range of SQL query types.
- Retries database connection once if it fails initially.
- Supports typed parameters and parameterized queries.
- Returns data for `SELECT` queries or affected row counts for `INSERT`, `UPDATE`, and `DELETE`.

{{ generate_block_details(page.title) }}

## Example(s)

### Example 1: Perform a SELECT query
- Create an `SQL` Block.
- Set the `connection_string` to connect to your database.
- Set the `query` to `SELECT * FROM employees WHERE department_id = :department_id`.
- Provide the parameter `department_id=10`.
- The Block will return the rows from the `employees` table where `department_id` is `10`.

### Example 2: Execute an INSERT query
- Set up an `SQL` Block.
- Use the `connection_string` to connect to your database.
- Set the `query` to `INSERT INTO employees (name, department_id) VALUES (:name, :department_id)`.
- Provide parameters `name="John Doe"` and `department_id=10`.
- The Block will insert a new row into the `employees` table and return the number of rows affected.

### Example 3: Update data with parameters
- Configure an `SQL` Block.
- Set the `query` to `UPDATE employees SET salary = :salary WHERE employee_id = :employee_id`.
- Provide parameters `salary=75000` and `employee_id=123`.
- The Block will update the salary of the specified employee and return the count of rows updated.

## Error Handling
- If the database connection fails initially, the Block will retry the connection once before raising an error.
- If required parameters are missing in the query, a `ValueError` will be raised, specifying the missing parameters.
- The Block will raise an error if the SQL syntax is invalid.

## FAQ

???+ question "What happens if the database connection fails?"

    The Block will attempt to reconnect once if the initial connection fails. If the reconnection also fails, it will raise a connection error.

???+ question "Can I use complex parameter types?"

    Yes, the Block supports various parameter types including integers, strings, floats, booleans, and dates. If a parameter is a list or tuple, it will be treated as an expanding parameter for `IN` queries.

???+ question "How does the Block handle different query types?"

    For `SELECT` queries, the Block returns rows as a list of dictionaries. For `INSERT`, `UPDATE`, `DELETE`, and similar queries, it returns the number of rows affected.

???+ question "Can I use this Block with any SQL database?"

    The Block is compatible with databases supported by SQLAlchemy’s `create_async_engine`. Ensure that your `connection_string` is in the correct format for your specific database.
