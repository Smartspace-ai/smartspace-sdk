from enum import Enum


class BlockCategory(Enum):
    # --- Active taxonomy ---
    AGENT = {
        "name": "Agent",
        "description": "LLM-driven, non-deterministic blocks",
    }
    DATA = {
        "name": "Data",
        "description": "Read, write, or search internal datasets, files, and embeddings",
    }
    WEB = {
        "name": "Web",
        "description": "Calls an external service over the network",
    }
    TRANSFORM = {
        "name": "Transform",
        "description": "Pure compute — reshape, parse, format, or convert data",
    }
    CONTROL = {
        "name": "Control",
        "description": "Routing, branching, looping, gating, and timing",
    }

    # --- Deprecated; kept for back-compat until all @metadata calls migrate ---
    # Remove these in a follow-up PR once both the SDK's own blocks and
    # downstream consumers (ai-api, etc.) have moved off them.
    FUNCTION = {"name": "Function", "description": "A callable entity"}
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
