{% set path = "assets/" + page.title + "-block.png" %}
{% if block_image_exists(path) %}
![{{page.title}}]({{path}}){{ block_image_sizing() }}
{% endif %}

## Overview

Parses tabular content (CSV/XLSX or markdown tables) into one JSON chunk per row and emits a single `Chunks` group. Handles mixed‑type columns by coercing to strings where needed and supports converting common document types to markdown tables via Document Intelligence.
## Description

(v2) Splits a table document into one JSON chunk per row, computes embeddings, and emits a single ChunkGroup containing all rows.

{{ generate_block_details_smartspace(page.title) }}
