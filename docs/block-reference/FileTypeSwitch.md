{% set path = "assets/" + page.title + "-block.png" %}
{% if block_image_exists(path) %}
![{{page.title}}]({{path}}){{ block_image_sizing() }}
{% endif %}

## Overview
Routes files to different outputs based on their file extension. Configure one or more named options with allowed extensions; when a file arrives, the first matching option emits the file to its output. If no option matches, the `default` output emits the file.

## Description

Routes a `File` to different outputs according to its extension. Each option declares a list of allowed types (e.g., pdf, docx, png). The block normalizes the extension (lower‑cased) from `file.name` and checks membership against configured types. If none match or the extension is unrecognized, the file is sent to `default`.

{{ generate_block_details_smartspace(page.title) }}

Additional notes:
- Options are configured as a mapping of `name -> { types, output }` in your graph (not simple config fields).
- Dynamic outputs: each configured option creates a named `output: File` port in addition to the `default` output.
- Supported FileType values include:
  - Text/markup: `txt`, `html`, `xml`, `json`, `yaml`, `csv`, `vtt`
  - Documents: `pdf`, `doc`, `docx`, `xls`, `xlsx`, `ppt`, `pptx`
  - Images: `jpeg`, `jpg`, `png`, `gif`, `bmp`, `tiff`
  - Markdown: `md`



## Example(s)

### Example 1: Route documents vs. images
- Configure options:
  - `documents`: `types=[doc, docx, pdf]` → connect to a document processing flow
  - `images`: `types=[png, jpg, jpeg]` → connect to an image pipeline
- Send `File(name="report.PDF")` → extension is normalized to `pdf` → routed to `documents`.

### Example 2: Fallback to default
- Only `images` option configured with `types=[png, jpg]`.
- Send `File(name="table.csv")` → no match → emitted to `default`.

### Example 3: Multiple overlapping groups
- `office`: `types=[docx, xlsx, pptx]`
- `presentations`: `types=[pptx]`
- A `File(name="deck.pptx")` will be sent to each matching option’s output (configure your graph to connect only one if you want single‑path routing).

## Error Handling
- If `file.name` has no extension, the file is sent to `default`.
- Unknown extensions or values not present in the `FileType` enum result in a `default` route.
- Option evaluation is best‑effort; an invalid option entry is skipped. Ensure `types` contain valid enum values.

## FAQ

???+ question "How do I add an output per extension?"

    Create an option entry with `types=[...]` and connect its `output` to downstream blocks. You can group multiple extensions under a single option.

???+ question "Is matching case‑sensitive?"

    No. The block lower‑cases the extension extracted from `file.name` before matching.

???+ question "What if a file matches multiple options?"

    Each matching option’s `output` is sent; structure the graph so only the intended path is connected if you need exclusive routing.

???+ question "Do I need to configure anything else?"

    No additional Config fields. Define `options` in your graph/editor and wire up the named outputs accordingly. The `default` output is always available.
