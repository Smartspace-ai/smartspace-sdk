from typing import Annotated, Generic, TypeVar

from smartspace.core import Config, GenericSchema, Tool

from app.integrations.llms.models import BaseChatFunction, BaseChatTool

RequestT = TypeVar("RequestT")
ResponseT = TypeVar("ResponseT")


class LLMTool(Tool, Generic[RequestT, ResponseT]):
    description: Annotated[str, Config()]
    schema: GenericSchema[RequestT]

    def run(self, request: RequestT) -> ResponseT: ...

    def create_tool(self, name: str):
        return BaseChatTool(
            type="function",
            function=BaseChatFunction(
                name=name,
                description=self.description,
                parameters={
                    "type": "object",
                    "properties": {"response": self.schema},
                    "required": ["response"],
                },
            ),
        )
