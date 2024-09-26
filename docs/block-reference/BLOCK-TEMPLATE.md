{% set path = "assets/" + page.title + "-block.png" %}
{% if block_image_exists(path) %}
![{{page.title}}]({{path}}){{ block_image_sizing() }}
{% endif %}

## Overview

{{ generate_block_details(page.title) }}    

## Example(s)

## Error Handling

## FAQ

