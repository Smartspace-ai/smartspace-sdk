# Block Documentation Guidelines

This document establishes standardized formatting and language conventions for all block descriptions and configuration parameters in the Smartspace AI workflow agent system.

## Overview

Consistent documentation ensures users can easily understand and configure blocks in the frontend interface. All block descriptions should be user-centric, actionable, and follow the templates below.

## Block Description Structure

### Template
```python
@metadata(
    category=BlockCategory.X,
    description="[Brief purpose statement] [Key capabilities in 1-2 bullet points] [Primary use case]",
    label="[5-7 searchable keywords separated by commas]"
)
```

### Guidelines
- **Length**: 3-4 sentences maximum (~200 characters)
- **Structure**: Purpose → Capabilities → Use case
- **Tone**: User-centric, action-oriented
- **Language**: Clear, accessible, avoid unnecessary jargon

### Examples

**Good:**
```python
description="Retrieves items from a dataset with optional filtering and sorting. Use this to fetch specific data based on conditions or get paginated results from large datasets."
```

**Avoid:**
```python
description="Retrieves dataset items with advanced SQL-style filtering and sorting capabilities. This block provides comprehensive data retrieval features including: • SQL-style property filtering with full operator support..."
```

## Configuration Parameter Structure

### Template
```python
parameter: Annotated[
    Type,
    Config(),
    Metadata(
        description="[What it does]. [Expected format/values]. [Example if helpful]."
    ),
] = default_value
```

### Guidelines
- **Length**: 1-2 sentences maximum (~100 characters)
- **Structure**: Function → Format → Example (if needed)
- **Focus**: What the user controls, not internal implementation
- **Examples**: Include only when format isn't obvious

### Examples

**Good:**
```python
description="Number of items to skip for pagination (default: 0). Used with take parameter to paginate through large result sets."
```

**Avoid:**
```python
description="""Number of items to skip from the beginning of results (default: 0). Used for pagination - e.g., skip=20 with take=10 gets items 21-30."""
```

## Label Keywords

### Template
```
"primary keyword, secondary keyword, action verb, use case, related term"
```

### Guidelines
- **Count**: 5-7 keywords maximum
- **Order**: Most important → least important
- **Style**: Lowercase, comma-separated
- **Content**: Mix of functionality, actions, and use cases

## Language Standards

### Terminology Dictionary
- **Dataset**: Collection of data items
- **Filter**: Condition to narrow results
- **Search**: Find items using text query
- **Retrieve**: Get specific items
- **Process**: Transform or analyze data
- **Generate**: Create new content
- **Parse**: Break down content into parts

### Voice and Tone
- **Active voice**: "Processes files" not "Files are processed"
- **Present tense**: "Retrieves data" not "Will retrieve data"
- **User-focused**: "Use this to..." not "This block enables..."
- **Direct**: Avoid hedging words like "allows", "enables", "provides"

## Category-Specific Guidelines

### DATA Blocks
- Focus on what data is accessed/modified
- Mention filtering, sorting, pagination when applicable
- Emphasize data source (dataset, file, etc.)

### AGENT/LLM Blocks
- Highlight AI capabilities and model interaction
- Mention tool usage, reasoning, or conversation features
- Focus on what the AI can help accomplish

### FUNCTION Blocks
- Emphasize the transformation or processing performed
- Mention input/output types when relevant
- Focus on the practical utility

### MISC Blocks
- Clear about specific utility or integration
- Mention file formats, external services, etc.
- Focus on when/why to use

## Implementation Checklist

When updating block documentation:

- [ ] Description follows 3-4 sentence structure
- [ ] Language is user-centric and actionable
- [ ] Configuration parameters are concise (1-2 sentences)
- [ ] Labels include 5-7 relevant keywords
- [ ] Terminology matches the dictionary
- [ ] Examples are simple and practical
- [ ] No technical jargon without explanation
- [ ] Focuses on user benefits, not implementation details

## Version History

- **v1.0** (2025-01-15): Initial guidelines established
- Future updates will be tracked here

---

*This document should be updated whenever new patterns or standards emerge for block documentation.*