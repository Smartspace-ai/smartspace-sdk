{% set path = "assets/" + page.title + "-block.png" %}
{% if block_image_exists(path) %}
![{{page.title}}]({{path}}){{ block_image_sizing() }}
{% endif %}

## Overview

Scrapes a base website using a headless browser, following internal links up to `page_limit`. Emits raw page content and structured page details (title, url, content), normalizing URLs without a scheme to `https://` by default.
## Description

Scrapes the content of a website using a headless browser.

Notes:
- This version delegates crawling/rendering to a shared headless browser service and returns fully rendered page text.
- If `base_url` lacks a scheme, the block prepends `https://` automatically.

## Metadata

- **Category**: Misc
- **Icon**: fa-globe
- **Label**: website scraper, web crawler, content extractor, web harvester, site parser

## Configuration Options

| Name | Data Type | Description | Default Value |
|------|-----------|-------------|---------------|
| page_limit | `int` | Maximum number of pages to crawl within the same domain | `3` |

## Inputs

| Name | Data Type | Description |
|------|-----------|-------------|
| base_url | `str` | The starting URL to crawl (scheme optional) |

## Outputs

| Name | Data Type | Description |
|------|-----------|-------------|
| website_content | `list[str]` | Raw text content for each visited page (one entry per page) |
| website_details | `list[WebDataBaseModel]` | Page details: `title`, `url`, and `content` |

## State Variables

No state variables available.



## Example(s)

### Example 1: Basic crawl with default page limit
- Config: `page_limit=3`
- Input: `base_url="example.com"` (no scheme provided)
- Output:
  - `website_content`: list of `str` (page texts)
  - `website_details`: list of `WebDataBaseModel` with `title`, `url`, `content`

### Example 2: Restrict to a single page
- Config: `page_limit=1`
- Input: `base_url="https://docs.mysite.io"`
- Output: contents and details for the root page only.
## Error Handling

- If `base_url` lacks a scheme, it is normalized to `https://<base_url>`.
- If the headless browser fails or returns no details, the block emits an empty `website_details` list and `website_content` with a single empty string.
- Network errors and page parsing failures are handled by the headless browser service; this block propagates failures only if the service raises.

## FAQ

???+ question "Does it handle client-side rendered pages?"

    Yes. The headless browser executes client-side rendering before extracting text.

???+ question "Does it crawl external domains?"

    The underlying service should restrict traversal to the same domain; only internal links are followed up to `page_limit`.
## FAQ

???+ question "Does it scrape external domains?"

    The underlying headless browser service should restrict traversal to the same domain. The block passes the `base_url` and `page_limit`; cross‑domain behavior depends on service implementation.

???+ question "How are dynamic pages handled?"

    Because it uses a headless browser, client‑side rendering is typically executed before extraction, improving coverage for SPAs.

???+ question "What fields do `website_details` include?"

    Typically `title`, `url`, and `content`. Additional metadata may be included depending on the service.
