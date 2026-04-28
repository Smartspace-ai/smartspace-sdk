from enum import Enum


class BlockCategory(Enum):
    AGENT = {"name": "Agent", "description": "An entity that performs actions"}
    FUNCTION = {"name": "Function", "description": "A callable entity"}
    DATA = {"name": "Data", "description": "A data entity"}
    CUSTOM = {"name": "Custom", "description": "A custom entity"}
    MISC = {"name": "Misc", "description": "Doesnt belong to any category"}


class FlowVariableAccess(Enum):
    NONE = "None"
    READ = "Read"
    WRITE = "Write"


class BlockClass(Enum):
    MODEL = "Model"
    OPERATOR = "Operator"


class ChannelEvent(Enum):
    DATA = "Data"
    CLOSE = "Close"


class ChannelState(Enum):
    OPEN = "Open"
    CLOSED = "Closed"


class StreamingEvent(Enum):
    """Events emitted by a StreamingOutput pin.

    UPDATE   — progressive snapshot of a single logical value. Supersedes
               any prior UPDATE on the same pin. Routes to FlowOutputs only
               (compute consumers see the FINALIZE value).
    FINALIZE — terminal, authoritative value. Fires once. Routes to
               FlowOutputs, FlowVariables and downstream FlowBlocks.
    """

    UPDATE = "Update"
    FINALIZE = "Finalize"


class BlockScope(Enum):
    WORKSPACE = "WorkSpace"
    DATASET = "DataSet"


class InputDisplayType(Enum):
    TEMPLATEOBJECT = "TemplateObject"
