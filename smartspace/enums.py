from enum import Enum


class BlockCategory(Enum):
    AGENT = {"name": "Agent", "description": "An entity that performs actions"}
    FUNCTION = {"name": "Function", "description": "A callable entity"}
    DATA = {"name": "Data", "description": "A data entity"}
    CUSTOM = {"name": "Custom", "description": "A custom entity"}
    MISC = {"name": "Misc", "description": "Doesnt belong to any category"}


class ChannelEvent(Enum):
    DATA = "Data"
    CLOSE = "Close"


class ChannelState(Enum):
    OPEN = "Open"
    CLOSED = "Closed"
