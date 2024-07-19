from enum import Enum


class BlockCategory(Enum):
    AGENT = {"name": "Agent", "description": "An entity that performs actions"}
    FUNCTION = {"name": "Function", "description": "A callable entity"}
    DATA = {"name": "Data", "description": "A data entity"}
    CUSTOM = {"name": "Custom", "description": "A custom entity"}
