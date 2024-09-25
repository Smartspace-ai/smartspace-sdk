"""
Basic example of a Mkdocs-macros module
"""

import math
import os

from docs.utils.block_doc_generator import (
    generate_block_markdown_details,
)


def define_env(env):
    """
    This is the hook for defining variables, macros and filters

    - variables: the dictionary that contains the environment variables
    - macro: a decorator function, to declare a macro.
    - filter: a function with one of more arguments,
        used to perform a transformation
    """

    # add to the dictionary of variables available to markdown pages:
    env.variables["baz"] = "John Doe"

    # NOTE: you may also treat env.variables as a namespace,
    #       with the dot notation:
    env.variables.baz = "John Doe"

    @env.macro
    def bar(x):
        return (2.3 * x) + 7

    # If you wish, you can  declare a macro with a different name:
    def f(x):
        return x * x

    env.macro(f, "barbaz")

    # or to export some predefined function
    env.macro(math.floor)  # will be exported as 'floor'

    # create a jinja2 filter
    @env.filter
    def reverse(x):
        "Reverse a string (and uppercase)"
        return x.upper()[::-1]

    @env.macro
    def generate_block_details(block_name: str):
        return generate_block_markdown_details(block_name)

    @env.macro
    def generate_block_details_smartspace(block_name: str):
        return generate_block_markdown_details(block_name, True)

    @env.macro
    def block_image_exists(path: str):
        full_path = os.path.join("docs", "block-reference", path)
        return os.path.exists(full_path)

    @env.macro
    def block_image_sizing():
        return '{: style="height:150px"}'
