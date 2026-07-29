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


class InputLanguage(Enum):
    """The language a string Config pin holds.

    A render hint for the flow designer: it selects the code editor's grammar,
    so the pin gets syntax highlighting, completion and inline errors instead of
    a plain text box. Purely presentational — nothing at runtime reads it.

    Distinct from InputDisplayType, which selects *which widget* renders a pin;
    this selects *which grammar* the text is in.

    Stamped automatically for fields marked Templatable() (JINJA) or
    Expression() (JMESPATH). Set it explicitly with Metadata(language=...) on
    pins that carry a language without using those markers.

    Consumers must treat an unrecognised value as plain text — blocks built
    against a newer SDK will emit languages an older designer doesn't know.
    """

    JMESPATH = "jmespath"
    JINJA = "jinja"
    JSONPATH = "jsonpath"
    DATASET_FILTER = "datasetFilter"
    DATASET_SORT = "datasetSort"
    SQL = "sql"
    PYTHON = "python"
    JSON = "json"
