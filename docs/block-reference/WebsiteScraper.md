{% set path = "assets/" + page.title + "-block.png" %}
{% if block_image_exists(path) %}
![{{page.title}}]({{path}}){{ block_image_sizing() }}
{% endif %}

## Overview
The `WebsiteScraper` Block scrapes the content of a given website and retrieves both raw content and metadata about the pages visited. This Block is ideal for extracting text from websites for analysis or processing, with options to limit the number of pages visited.

{{ generate_block_details(page.title) }}

## Example(s)

### Example 1: Scrape content from a website
- Create a `WebsiteScraper` Block.
- Provide the base URL, such as `"https://example.com"`.
- Set the `page_limit` configuration to `3`.
- The Block will output:
  - `website_content`: A list of raw text content from the pages.
  - `website_details`: A list of detailed metadata, including the title, URL, and content of each page.

### Example 2: Limit the number of pages to scrape
- Set up a `WebsiteScraper` Block.
- Provide a base URL and set `page_limit` to `1`.
- The Block will scrape only the specified page and output its content and metadata.

## Error Handling
- If the URL is invalid or unreachable, the Block will log an error and skip the page.
- If no pages are successfully scraped, the Block will output empty lists for both `website_content` and `website_details`.

## FAQ

???+ question "Can the Block scrape multiple pages from a website?"

    Yes, the Block will scrape the base URL and additional pages linked from it, up to the `page_limit` configuration. Only pages within the same domain as the base URL will be scraped.

???+ question "What happens if the base URL is empty or invalid?"

    If the base URL is empty, the Block will output empty results. For invalid or unreachable URLs, the Block will log an error and skip the page.

???+ question "How does the Block handle rate limiting?"

    The Block uses a short delay (`1 second`) between batches of scraping tasks to avoid overwhelming the server. 

    
???+ question "What metadata is included in the `website_details` output?"

    The `website_details` output includes the following for each page:
    - `title`: The title of the webpage.
    - `url`: The URL of the webpage.
    - `content`: The text content extracted from the page, excluding scripts and styles.