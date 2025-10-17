{% set path = "assets/" + page.title + "-block.png" %}
{% if block_image_exists(path) %}
![{{page.title}}]({{path}}){{ block_image_sizing() }}
{% endif %}

## Overview
Agent-driven template filling with validation and optional DOCX generation. Processes multiple named sections in parallel using your selected LLM, validates outputs for conflicts, and re-runs only the flagged sections (up to 4 attempts per section). Produces a final structured data object, optional markdown preview, and an optional DOCX generated from a template.

## Description

Processes sections by streaming data, validating conflicts, and re-running only flagged sections up to 4 attempts (parallel reruns count as one). Merges into final schema/data output and optionally generates DOCX.

Notes:
- Sections run in parallel on the first pass; only failing sections are re-run in subsequent validation rounds.
- Validation combines LLM-based checks with programmatic formatting checks (e.g., code blocks, headings) against your base prompt instructions.
- When configured, generates a DOCX using a provided template; otherwise it can emit a markdown preview.

## Metadata

- **Category**: Agent
- **Label**: template-filler-with-validation

## Configuration Options

| Name | Data Type | Description | Default Value |
|------|-----------|-------------|---------------|
| modelId | `str` | Model identifier used by the LLM service | (required) |
| sections | `List[Section]` | List of sections to generate; each section has `label`, `pre_prompt`, and `schema` (default type string) |  |
| template | `TemplateConfig` | DOCX generation config. Fields: `file: File`, `name: str` (Jinja), `preview: str` (markdown Jinja) |  |
| BasePrompt.basePrompt | `str` | Common pre‑prompt shared by all sections; supports Jinja with `**context` | `""` |

## Inputs

| Name | Data Type | Description |
|------|-----------|-------------|
| start | `None` | Trigger input to start processing |
| message | `str` | User message or task description passed to the LLM |
| **context | `Any` | Arbitrary key/values available to Jinja in `BasePrompt`, section `pre_prompt`, and template fields |

## Outputs

| Name | Data Type | Description |
|------|-----------|-------------|
| data | `Dict[str, Any]` | Final structured data keyed by section `label` |
| file | `File` | Generated DOCX (when `template.file` is provided) |
| markdown | `str` | Rendered markdown preview (when `template.preview` provided) |
| response | `str` | Manager‑style summary of the work completed |

## State Variables

| Name | Data Type | Description |
|------|-----------|-------------|
| collected_section_data | `Dict[str, Any]` | Accumulated section results across passes |
| final_schema_state | `Dict[str, Any]` | Aggregated schema from all sections |
| generated_document_state | `File or Constant(value=None)` | Last generated DOCX (if any) |
| formatted_message_state | `str or Constant(value=None)` | Last rendered manager summary |



## Example(s)

### Example 1: Two sections with DOCX and preview
- Config:
  - `modelId="gpt-4o-mini"`
  - `BasePrompt.basePrompt="You are drafting a product brief for {% raw %}{{company}}{% endraw %}."`
  - `sections=[
      {label: "title", pre_prompt: "Write a concise title", schema: {"type": "string"}},
      {label: "summary", pre_prompt: "Write a 120-word summary", schema: {"type": "string"}}
    ]`
  - `template={ file: <docx template File>, name: "{% raw %}{{ title }}{% endraw %}_Brief", preview: "# {% raw %}{{ title }}{% endraw %}\n\n{% raw %}{{ summary }}{% endraw %}" }`
- Inputs:
  - `message="We’re launching an AI note-taking app."`
  - `context={"company": "Acme"}`
- Outputs:
  - `data={"title": "...", "summary": "..."}`
  - `markdown="# <title>\n\n<summary>"`
  - `file=<File name="<title>_Brief.docx">`
  - `response="Work completed: ..."`

### Example 2: Validation and selective re-runs
- If validation flags the `summary` section (e.g., too long or formatting issues), only `summary` is re-run with feedback up to 4 attempts, while `title` remains as is.

### Example 3: No DOCX, preview only
- Omit `template.file` but set `template.preview` to a markdown Jinja template to emit a formatted preview without generating a document.

## Error Handling
- Missing dataset artifacts: If `template.file` is set but cannot be fetched, document generation fails with a descriptive error; other outputs continue.
- Invalid Jinja in `template.name` or `template.preview` raises a template error during render.
- Section call failures raise exceptions from the LLM service; validation failures fallback to no issues and proceed with current data.
- DOCX generation uses `docxtpl`; invalid or empty templates raise a clear error.

## FAQ

???+ question "How many times can a section be re-run?"

    Up to 4 attempts per section. Each parallel batch of re-runs counts as one attempt per section included.

???+ question "What does validation check?"

    A combination of LLM-based validation (instruction compliance, content accuracy, schema adherence) and programmatic formatting checks (e.g., fenced code blocks, headings) using your base prompt.

???+ question "Can I use context variables in prompts and template names?"

    Yes. `BasePrompt.basePrompt`, section `pre_prompt`, and `template.name`/`template.preview` support Jinja with the `**context` you pass to the step.

???+ question "What does the `response` output contain?"

    A concise, manager-style summary of what was generated, conflicts found/resolved, and deliverables (preview/document).
