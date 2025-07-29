{% set path = "assets/" + page.title + "-block.png" %}
{% if block_image_exists(path) %}
![{{page.title}}]({{path}}){{ block_image_sizing() }}
{% endif %}

## Overview
The `SQL` Block executes SQL queries on databases using SQLAlchemy with ODBC connectivity. It supports all types of SQL operations including SELECT, INSERT, UPDATE, and DELETE queries. The Block handles both data retrieval and data modification operations, automatically managing transactions and returning appropriate results.

For SELECT queries, the Block returns a list of dictionaries representing the rows. For data-modifying queries (INSERT, UPDATE, DELETE), it returns the number of affected rows. The Block uses parameterized queries for security and supports various data types with automatic type mapping.

{{ generate_block_details(page.title) }}

## Example(s)

### Example 1: Execute a SELECT query
- Create a `SQL` Block.
- Configure connection string: `"mssql+aioodbc://user:pass@server:1433/db?driver=ODBC+Driver+18+for+SQL+Server"`.
- Configure query: `"SELECT name, age FROM users WHERE active = :active"`.
- Provide parameters: `{"active": true}`.
- The Block will output: `[{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]`.

### Example 2: Insert new records
- Set up a `SQL` Block.
- Configure connection string and query: `"INSERT INTO users (name, email) VALUES (:name, :email)"`.
- Provide parameters: `{"name": "Charlie", "email": "charlie@example.com"}`.
- The Block will output: `1` (number of affected rows).

### Example 3: Update existing records
- Create a `SQL` Block.
- Configure query: `"UPDATE products SET price = :price WHERE category = :category"`.
- Provide parameters: `{"price": 29.99, "category": "electronics"}`.
- The Block will output the number of updated rows.

### Example 4: Query with multiple parameters
- Set up a `SQL` Block.
- Configure query: `"SELECT * FROM orders WHERE date >= :start_date AND date <= :end_date AND status = :status"`.
- Provide parameters: `{"start_date": "2024-01-01", "end_date": "2024-12-31", "status": "completed"}`.
- The Block will return matching order records.

### Example 5: Use expanding parameters for IN clauses
- Create a `SQL` Block.
- Configure query: `"SELECT * FROM users WHERE id IN :user_ids"`.
- Provide parameters: `{"user_ids": [1, 2, 3, 4]}`.
- The Block will expand the list for the IN clause and return matching users.

## Error Handling
- The Block validates that all required parameters are provided. Missing parameters will raise a `ValueError` with details about which parameters are missing.
- Database connection failures are handled gracefully, with descriptive error messages for common issues like incorrect connection strings or unreachable servers.
- SQL syntax errors and constraint violations are caught and reported with relevant database error details.
- The Block automatically handles transaction management, committing successful data-modifying operations and rolling back on errors.
- Parameter type mismatches are handled through automatic type mapping, with fallback to string types for unsupported types.

## FAQ

???+ question "What database systems are supported?"

    The `SQL` Block uses SQLAlchemy, so it supports any database that has an async SQLAlchemy driver. Common examples include SQL Server (via aioodbc), PostgreSQL (via asyncpg), MySQL (via aiomysql), and SQLite (via aiosqlite).

???+ question "How do I format the connection string?"

    Connection strings follow SQLAlchemy format. For SQL Server: `"mssql+aioodbc://user:pass@server:port/database?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes"`. For PostgreSQL: `"postgresql+asyncpg://user:pass@host:port/database"`.

???+ question "Can I use this Block for stored procedures?"

    Yes, you can execute stored procedures using the appropriate SQL syntax for your database system (e.g., `"EXEC procedure_name :param1, :param2"` for SQL Server).

???+ question "How are parameters handled for security?"

    The Block uses SQLAlchemy's parameterized queries, which automatically handle SQL injection protection. All parameters are properly escaped and typed before execution.

???+ question "What happens if a query returns no results?"

    For SELECT queries that return no results, the Block will output an empty list `[]`. For data-modifying queries that affect no rows, it will return `0`.

???+ question "Can I execute multiple statements in one query?"

    This depends on your database system and driver configuration. Some systems support multiple statements separated by semicolons, while others require separate Block executions for security reasons.

???+ question "How does the Block handle different data types?"

    The Block automatically maps Python types to appropriate SQL types (str→String, int→Integer, float→Float, bool→Boolean, datetime→DateTime, etc.). Complex types are handled through SQLAlchemy's type system.

???+ question "What happens if the database connection fails?"

    The Block will attempt to establish the connection and provide detailed error messages for connection failures. Common issues include incorrect credentials, unreachable servers, or missing database drivers.

???+ question "Can I use transactions explicitly?"

    The Block automatically manages transactions. Data-modifying queries are committed automatically on success and rolled back on error. For complex multi-statement transactions, consider using database-specific transaction syntax in your queries.

