import enum
from datetime import datetime
from typing import Annotated, Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

from smartspace.enums import ChannelEvent, ChannelState
from smartspace.utils import _get_type_adapter


class PinType(enum.Enum):
    SINGLE = "Single"
    LIST = "List"
    DICTIONARY = "Dictionary"


class PortType(enum.Enum):
    SINGLE = "Single"
    LIST = "List"
    DICTIONARY = "Dictionary"


class BlockPinRef(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    port: str
    pin: str


class InputPinInterface(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    metadata: dict[str, Any] = {}
    sticky: bool
    json_schema: Annotated[dict[str, Any], Field(alias="schema")]
    generics: dict[
        str, BlockPinRef
    ]  # Name of the generic, like OutputT, and then a reference to the input on this block that defines the schema
    type: PinType
    required: bool
    default: Any
    channel: bool
    virtual: bool


class OutputPinInterface(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    metadata: dict[str, Any] = {}
    json_schema: Annotated[dict[str, Any], Field(alias="schema")]
    generics: dict[
        str, BlockPinRef
    ]  # Name of the generic, like OutputT, and then a reference to the input on this block that defines the schema
    type: PinType
    channel: bool
    channel_group_id: Annotated[str | None, Field(alias="channelGroupId")]


class PortInterface(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    metadata: dict[str, Any] = {}
    inputs: dict[str, InputPinInterface]
    outputs: dict[str, OutputPinInterface]
    type: PortType
    is_function: Annotated[bool, Field(alias="isFunction")]


class StateInterface(BaseModel):
    """
    scope_pins is a list of pins that set the scope of the state.
    When any function runs, state is set on the component.
    And for each run that the scope_pins have the same values, that state will be reused
    """

    model_config = ConfigDict(populate_by_name=True)

    metadata: dict[str, Any] = {}
    scope: list[BlockPinRef]
    default: Any


class FunctionInterface(BaseModel):
    model_config = ConfigDict(populate_by_name=True)


class BlockInterface(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    metadata: dict[str, Any] = {}
    ports: dict[str, PortInterface]
    state: dict[str, StateInterface]


class FlowContext(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    workspace: "SmartSpaceWorkspace | None"
    message_history: "list[ThreadMessage] | None"


class BlockErrorModel(BaseModel):
    message: str
    data: Any


class InputValue(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    target: BlockPinRef
    value: Any


class OutputValue(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    source: BlockPinRef
    value: Any


class StateValue(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    state: str
    value: Any


class PinRedirect(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    source: BlockPinRef
    target: BlockPinRef


class ThreadMessageResponseSource(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    index: int
    uri: str


class ThreadMessageResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    content: str
    sources: list[ThreadMessageResponseSource] | None = None


class File(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    name: str | None = None


class ContentItem(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    image: File | None = None
    text: str | None = None


class ThreadMessage(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    content: str | None = None
    content_list: Annotated[list[ContentItem] | None, Field(alias="contentList")] = None
    response: ThreadMessageResponse
    created_at: Annotated[datetime, Field(..., alias="createdAt")]
    created_by: Annotated[str, Field(..., alias="createdBy")]


class SmartSpaceDataSpace(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    name: str


class SmartSpaceWorkspace(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    name: str
    data_spaces: Annotated[list[SmartSpaceDataSpace], Field(alias="dataSpaces")] = []
    flow_definition: Annotated[
        "FlowDefinition | None", Field(alias="flowDefinition")
    ] = None

    @property
    def dataspace_ids(self) -> list[str]:
        return [dataspace.id for dataspace in self.data_spaces]


class FlowPinRef(BaseModel):
    """
    When referencing block pins, block, port, and pin must be set
    When referencing a constant, only block must be set
    """

    model_config = ConfigDict(populate_by_name=True)

    node: str
    port: str | None = None
    pin: str | None = None


class Connection(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    source: FlowPinRef
    target: FlowPinRef


class FlowBlock(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str
    version: str
    dynamic_ports: Annotated[list[str], Field(alias="dynamicPorts")] = []
    dynamic_output_pins: Annotated[
        list[BlockPinRef], Field(alias="dynamicOutputPins")
    ] = []
    dynamic_input_pins: Annotated[
        list[BlockPinRef], Field(alias="dynamicInputPins")
    ] = []


class FlowConstant(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    value: Any


class FlowInput(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    json_schema: Annotated[dict[str, Any], Field(alias="schema")]

    @classmethod
    def from_type(cls, t: type) -> "FlowInput":
        return FlowInput(json_schema=_get_type_adapter(t).json_schema())


class FlowOutput(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    json_schema: Annotated[dict[str, Any], Field(alias="schema")]

    @classmethod
    def from_type(cls, t: type) -> "FlowOutput":
        return FlowOutput(json_schema=_get_type_adapter(t).json_schema())


class FlowDefinition(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    inputs: dict[str, FlowInput]
    outputs: dict[str, FlowOutput]
    constants: dict[str, FlowConstant]
    blocks: dict[str, FlowBlock]

    connections: list[Connection]

    def get_source_node(self, node: str) -> FlowBlock | FlowInput | FlowConstant | None:
        return (
            self.inputs.get(node, None)
            or self.constants.get(node, None)
            or self.blocks.get(node, None)
        )

    def get_target_node(self, node: str) -> FlowBlock | FlowOutput | None:
        return self.outputs.get(node, None) or self.blocks.get(node, None)


class BlockRunData(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str
    version: str
    function: str
    context: FlowContext | None
    state: list[StateValue] | None
    inputs: list[InputValue] | None
    dynamic_ports: list[str] | None
    dynamic_output_pins: list[BlockPinRef] | None
    dynamic_input_pins: list[BlockPinRef] | None


class BlockRunMessage(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    outputs: list[OutputValue] = []
    inputs: list[InputValue] = []
    redirects: list[PinRedirect] = []
    states: list[StateValue] = []


ChannelT = TypeVar("ChannelT")


class InputChannel(BaseModel, Generic[ChannelT]):
    model_config = ConfigDict(populate_by_name=True)

    state: ChannelState
    event: ChannelEvent | None
    data: ChannelT | None


class OutputChannelMessage(BaseModel, Generic[ChannelT]):
    model_config = ConfigDict(populate_by_name=True)

    event: ChannelEvent | None
    data: ChannelT | None
