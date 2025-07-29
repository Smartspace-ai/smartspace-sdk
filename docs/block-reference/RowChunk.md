{% set path = "assets/" + page.title + "-block.png" %}
{% if block_image_exists(path) %}
![{{page.title}}]({{path}}){{ block_image_sizing() }}
{% endif %}

## Overview
The `RowChunk` Block splits a table document into one chunk per row. It can process various table formats including CSV files, Excel spreadsheets (XLSX), and markdown tables. The output is a list of chunks, each containing a row of the table in JSON format. This block is useful for processing tabular data row by row, enabling downstream processing of individual records.

{{ generate_block_details_smartspace(page.title) }}

## Example(s)

### Example 1: Process a CSV file
- Create a `RowChunk` Block.
- Provide a CSV File object as input.
- The Block will read the CSV and create one chunk per row.
- Each chunk contains the row data as a JSON string with column names as keys.

### Example 2: Process an Excel file with multiple sheets
- Create a `RowChunk` Block.
- Provide an XLSX File object.
- The Block will process all sheets, creating chunks for each row across all sheets.
- Empty rows are automatically skipped.

### Example 3: Process a markdown table string
- Create a `RowChunk` Block.
- Provide a markdown table string: 
  ```
  | Name | Age | City |
  | John | 25 | NYC |
  | Jane | 30 | LA |
  ```
- The Block will parse the table and create chunks for each data row.

### Example 4: Process complex documents
- Create a `RowChunk` Block.
- Provide a PDF or DOCX file containing tables.
- The Block will first convert the document to markdown using document intelligence.
- Then extract and chunk any tables found in the content.

## Error Handling
- If an unsupported file type is provided, the Block will raise a `BlockError`.
- Mixed data types in columns are automatically converted to strings to ensure consistency.
- The Block handles missing values (NaN) appropriately, skipping empty rows.

## FAQ

???+ question "What file formats are supported?"

    Directly supported:
    - **CSV**: Comma-separated values files
    - **XLSX**: Excel spreadsheets (all sheets are processed)
    - **Markdown tables**: String input with pipe-delimited tables
    
    Via document intelligence conversion:
    - **Images**: JPEG, JPG, PNG, BMP, TIFF, HEIF
    - **Documents**: DOCX, PPTX, PDF

???+ question "How are data types handled?"

    The Block automatically handles mixed data types in columns:
    - If a column contains multiple data types, all values are converted to strings
    - Pandas Timestamps are converted to string representation
    - NaN/null values are preserved where possible

???+ question "What's the output format?"

    Each chunk contains:
    - `name`: Filename with row index (e.g., "data.csv[0]")
    - `index`: Row number
    - `position`: Same as index
    - `content`: JSON string of the row data with column names as keys

???+ question "How are large text values handled?"

    For CSV files with large text content, the Block uses sentence chunking to split long text values into manageable chunks while preserving the row structure.

???+ question "Can I process specific sheets in Excel files?"

    Currently, the Block processes all sheets in an Excel file. Each row is tagged with the source filename and row index, allowing you to filter results downstream if needed.