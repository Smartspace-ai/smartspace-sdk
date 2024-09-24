{% set path = "assets/" + page.title + "-block.png" %}
{% if block_image_exists(path) %}
![{{page.title}}]({{path}})
{% endif %}

## Overview

{{ generate_block_details_smartspace(page.title) }}    

## Example(s)

## Error Handling

## FAQ

