import enum
from datetime import datetime, timezone
from typing import Annotated, Any, ClassVar, Tuple
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    PlainSerializer,
    model_serializer,
)

from smartspace.utils import _get_type_adapter


class BlockReference(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    block_id: Annotated[str, Field(alias="blockId")]


class ToolReference(BlockReference):
    model_config = ConfigDict(populate_by_name=True)

    tool_id: Annotated[str, Field(alias="toolId")]


class StepReference(BlockReference):
    model_config = ConfigDict(populate_by_name=True)

    step_id: Annotated[str, Field(alias="stepId")]


class StepInputReference(StepReference):
    model_config = ConfigDict(populate_by_name=True)

    input_id: Annotated[str, Field(alias="inputId")]


class BlockOutputReference(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    block_id: Annotated[str, Field(alias="blockId")]
    output_id: Annotated[str, Field(alias="outputId")]


class ToolInputReference(ToolReference):
    model_config = ConfigDict(populate_by_name=True)

    input_id: Annotated[str, Field(alias="inputId")]


class ToolOutputReference(ToolReference):
    model_config = ConfigDict(populate_by_name=True)

    output_id: Annotated[str, Field(alias="outputId")]


class FlowInputReference(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    flow_input_id: Annotated[str, Field(alias="flowInputId")]


class FlowOutputReference(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    flow_output_id: Annotated[str, Field(alias="flowOutputId")]


class ChildFlowOutputReference(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    flow_id: Annotated[str, Field(alias="flowId")]
    flow_output_id: Annotated[str, Field(alias="flowOutputId")]


class ChildFlowInputReference(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    flow_id: Annotated[str, Field(alias="flowId")]
    flow_input_id: Annotated[str, Field(alias="flowInputId")]


class BlockType(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str
    version: str

    def __hash__(self):
        return hash((type(self),) + tuple(self.__dict__.values()))


class IOCInterface(BaseModel):
    """
    Base model for Inputs, Outputs, and Configs
    """

    name: str
    model_config = ConfigDict(populate_by_name=True)
    metadata: dict = {}

    json_schema: Annotated[dict[str, Any], Field(alias="jsonSchema")]


class InputInterface(IOCInterface):
    sticky: bool


class OutputInterface(IOCInterface): ...


class ConfigInterface(IOCInterface):
    default_value: Annotated[Any, Field(alias="defaultValue")]


class ToolInterface(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    metadata: dict = {}
    name: str
    multiple: bool
    inputs: Annotated[list[InputInterface], Field(min_length=1)]
    output: OutputInterface | None = None
    configs: list[ConfigInterface] | None = None

    @model_serializer
    def _serialize(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "name": self.name,
            "multiple": self.multiple,
            "metadata": self.metadata,
        }

        if len(self.inputs):
            d["inputs"] = self.inputs

        if self.output:
            d["output"] = self.output

        if self.configs is not None and len(self.configs):
            d["configs"] = self.configs

        return d


class StepInterface(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    metadata: dict = {}
    name: str
    inputs: Annotated[list[InputInterface], Field(min_length=1)]
    output_ref: Annotated[str | None, Field(None, alias="outputRef")]

    @model_serializer
    def _serialize(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "name": self.name,
            "inputs": self.inputs,
            "metadata": self.metadata,
        }

        if self.output_ref:
            d["outputRef"] = self.output_ref

        return d


class CallbackInterface(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str
    inputs: Annotated[list[InputInterface], Field(min_length=1)]


class StateInterface(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str
    step_id: Annotated[str | None, Field(alias="stepId")]
    input_ids: Annotated[list[str] | None, Field(alias="inputIds")]
    default_value_json: Annotated[str, Field(alias="defaultValueJson")]


class BlockInterface(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    metadata: dict = {}
    name: str
    version: str = "unknown"
    steps: list[StepInterface]
    callbacks: list[CallbackInterface] | None = None
    outputs: list[OutputInterface] | None = None
    configs: list[ConfigInterface] | None = None
    tools: list[ToolInterface] | None = None
    states: list[StateInterface] | None = None

    @model_serializer
    def _serialize(self) -> dict[str, Any]:
        d = {
            "name": self.name,
            "version": self.version,
            "steps": self.steps,
            "metadata": self.metadata,
        }
        if self.callbacks is not None and len(self.callbacks):
            d["callbacks"] = self.callbacks

        if self.outputs is not None and len(self.outputs):
            d["outputs"] = self.outputs

        if self.tools is not None and len(self.tools):
            d["tools"] = self.tools

        if self.configs is not None and len(self.configs):
            d["configs"] = self.configs

        return d


class FlowIODefinition(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str
    json_schema: Annotated[dict[str, Any], Field(alias="jsonSchema")]

    @classmethod
    def from_type(cls, name: str, t: type):
        return FlowIODefinition(
            name=name, json_schema=_get_type_adapter(t).json_schema()
        )


class ValueSourceType(enum.Enum):
    BLOCK_OUTPUT = "BlockOutput"
    TOOL_INPUT = "ToolInput"
    FLOW_INPUT = "FlowInput"
    CHILD_FLOW_OUTPUT = "ChildFlowOutput"
    CALLBACK_DIRECT_VALUE = "CallbackDirectValue"


class ValueSourceRef(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    type: Annotated[ValueSourceType, PlainSerializer(lambda t: t.value)]
    block_output: Annotated[BlockOutputReference | None, Field(alias="blockOutput")] = (
        None
    )
    step: Annotated[StepReference | None, Field(alias="step")] = None
    tool_input: Annotated[ToolInputReference | None, Field(alias="toolInput")] = None
    flow_input: Annotated[FlowInputReference | None, Field(alias="flowInput")] = None
    child_flow_output: Annotated[
        ChildFlowOutputReference | None, Field(alias="childFlowOutput")
    ] = None


class ValueTargetType(enum.Enum):
    STEP_INPUT = "StepInput"
    FLOW_OUTPUT = "FlowOutput"
    TOOL_OUTPUT = "ToolOutput"
    CHILD_FLOW_INPUT = "ChildFlowInput"


class ValueTargetRef(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    type: Annotated[ValueTargetType, PlainSerializer(lambda t: t.value)]
    step_input: Annotated[StepInputReference | None, Field(alias="stepInput")] = None
    flow_output: Annotated[FlowOutputReference | None, Field(alias="flowOutput")] = None
    tool_output: Annotated[ToolOutputReference | None, Field(alias="toolOutput")] = None
    child_flow_input: Annotated[
        ChildFlowInputReference | None, Field(alias="childFlowInput")
    ] = None


class ConnectionDefinition(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    source: ValueSourceRef
    target: ValueTargetRef


class FlowDefinition(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    class Block(BaseModel):
        id: str
        type: BlockType
        config: dict[
            str, Any
        ] = {}  # the keys in this must match configs in the BlockType
        tools: dict[str, Any] = {}

    inputs: list[FlowIODefinition]
    outputs: list[FlowIODefinition]
    connections: list[ConnectionDefinition]
    blocks: list[Block]
    children: dict[str, "FlowDefinition"] = {}


class FlowValueVersion(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: UUID
    value_source: Annotated[ValueSourceRef, Field(alias="valueSource")]
    parent_ids: Annotated[list[UUID], Field(alias="parentIds")]

    def is_descendant(self, other: "FlowValueVersion"):
        return any(
            [
                True if parent.id == other.id else parent.is_descendant(other)
                for parent in self.parents
            ]
        )

    @property
    def parents(self) -> list["FlowValueVersion"]:
        parents: list[FlowValueVersion] = []

        for parent_id in self.parent_ids:
            if parent_id not in FlowValueVersion._all_values:
                raise Exception(f"Missing FlowValueVersion with id {parent_id}")

            parents.append(self._all_values[parent_id])

        return parents

    _all_values: ClassVar[dict[UUID, "FlowValueVersion"]] = {}
    _histories_cache: ClassVar[
        dict[UUID, Tuple[datetime, list[Tuple[str, set[UUID]]]]]
    ] = {}

    # TODO this is dirty
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        FlowValueVersion._all_values[self.id] = self

    @property
    def source_id(self) -> str:
        """
        id is a hash of the value's source (block output or flow input) and the entire history of the value
        Each item in the history is id and the version.
        So for 2 FlowValueVersion objects, they will have the same id only if they were generated by the same execution of a step and sent out the same output
        The only difference between them would then be the version
        """
        existing_value = getattr(self, "_source_id", None)
        if existing_value is not None:
            return existing_value

        if self.value_source.flow_input:
            source_str = self.value_source.flow_input.flow_input_id
        elif self.value_source.tool_input:
            source_str = (
                self.value_source.tool_input.block_id
                + self.value_source.tool_input.tool_id
                + self.value_source.tool_input.input_id
            )
        elif self.value_source.block_output:
            source_str = (
                self.value_source.block_output.block_id
                + self.value_source.block_output.output_id
            )
        elif self.value_source.step:
            source_str = (
                self.value_source.step.block_id + self.value_source.step.step_id
            )
        else:
            raise Exception(f"Unexpected value source type {self.value_source.type}")

        id = source_str + "".join(str(self.parent_ids))

        setattr(self, "_source_id", id)

        return id

    @property
    def version_history(
        self,
    ) -> list[Tuple[str, set[UUID]]]:  # list of (value.source_id, [version numbers])
        if self.id in FlowValueVersion._histories_cache:
            return FlowValueVersion._histories_cache[self.id][1]

        versions_dict: dict[str, set[UUID]] = {}

        for parent in self.parents:
            for version_id, version_list in parent.version_history:
                if version_id in versions_dict:
                    versions_dict[version_id].union(version_list)
                else:
                    versions_dict[version_id] = set(
                        version_list
                    )  # creating a copy of the set, just to be safe

        versions_dict[self.source_id] = set([self.id])

        versions = [
            (version_id, version_list)
            for version_id, version_list in versions_dict.items()
        ]
        versions.sort(reverse=True)  # descending

        # TODO this caching system could be improved, maybe versionnhistory can be improved in general

        if len(FlowValueVersion._histories_cache) > 100:
            items = [(v[0], k) for k, v in FlowValueVersion._histories_cache.items()]
            items.sort()
            for _, key in items[:50]:
                del FlowValueVersion._histories_cache[key]

        FlowValueVersion._histories_cache[self.id] = (
            datetime.now(timezone.utc),
            versions,
        )

        return versions

    def is_same_branch(self, other: "FlowValueVersion") -> bool:
        """
        Checks the tree for both flow values and checks if they are on the same branch
        If either has a matching FlowValueVersion in it's history with just a different version, they are not compatible as they are on different branches
        """
        i = 0
        j = 0

        self_versions = self.version_history
        other_versions = other.version_history

        while (
            i < len(self_versions) and j < len(other_versions)
        ):  # version lists are sorted. This does a single pass through both to find matches
            if self_versions[i][0] < other_versions[j][0]:
                j += 1
            elif self_versions[i][0] > other_versions[j][0]:
                i += 1
            else:
                if self_versions[i][1] != other_versions[j][1]:
                    return False
                i += 1
                j += 1

        return True


class FlowValue(FlowValueVersion):
    value: Any


class CallbackCall(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    callback_name: str
    direct_params: dict[str, Any]
    tool_result_param: str


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

    name: str | None = None
    uri: str


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
    flow_definition: Annotated[FlowDefinition | None, Field(alias="flowDefinition")] = (
        None
    )

    @property
    def dataspace_ids(self) -> list[str]:
        return [dataspace.id for dataspace in self.data_spaces]


class FlowContext(BaseModel):
    workspace: SmartSpaceWorkspace | None
    message_history: list[ThreadMessage] | None


class InputDefinition(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    metadata: dict = {}
    id: str
    json_schema: Annotated[dict[str, Any], Field(alias="jsonSchema")]
    sticky: bool


class OutputDefinition(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    metadata: dict = {}

    id: str
    json_schema: Annotated[dict[str, Any], Field(alias="jsonSchema")]


class ToolInputDefinition(OutputDefinition):
    model_config = ConfigDict(populate_by_name=True)
    metadata: dict = {}

    tool_id: Annotated[str, Field(alias="toolId")]


class ToolOutputDefinition(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    metadata: dict = {}

    id: str
    tool_id: Annotated[str, Field(alias="toolId")]
    json_schema: Annotated[dict[str, Any], Field(alias="jsonSchema")]


class StepDefinition(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    metadata: dict = {}

    id: str
    inputs: dict[str, InputDefinition]
    output: OutputDefinition | None


class ConfigDefinition(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    value: Any


class ToolDefinition(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    metadata: dict = {}
    id: str
    inputs: dict[str, ToolInputDefinition]
    output: ToolOutputDefinition | None
    configs: dict[str, ConfigDefinition]


class StateDefinition(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    value: Any


class BlockDefinition(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    metadata: dict = {}
    id: str
    type: BlockType
    configs: dict[str, ConfigDefinition]
    outputs: dict[str, OutputDefinition]
    steps: dict[str, StepDefinition]
    tools: dict[str, ToolDefinition]
    states: dict[str, StateDefinition]


class DebugBlockRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    block_definition: Annotated[BlockDefinition, Field(alias="blockDefinition")]
    flow_context: Annotated[FlowContext, Field(alias="flowContext")]
    step_id: Annotated[str, Field(alias="stepId")]
    inputs: dict[str, FlowValue]


class DebugBlockResult(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    class Callback(BaseModel):
        model_config = ConfigDict(populate_by_name=True)

        tool_id: Annotated[str, Field(alias="toolId")]
        tool_call_values: Annotated[list[FlowValue], Field(alias="toolCallValues")]
        callback: CallbackCall

    states: dict[str, Any]
    outputs: list[FlowValue]
    callbacks: list[Callback]
