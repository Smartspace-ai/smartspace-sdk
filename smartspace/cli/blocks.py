import uuid
from typing import Any

import typer
from more_itertools import first

from smartspace.core import Block
from smartspace.models import (
    BlockInterface,
    CallbackCall,
    DebugBlockRequest,
    DebugBlockResult,
    FlowValue,
    ValueSourceRef,
)

app = typer.Typer()


@app.command()
def debug(path: str = "", poll: bool = False):
    import asyncio
    import os
    from contextlib import suppress

    from pysignalr.client import SignalRClient
    from pysignalr.messages import (
        CompletionMessage,
        HandshakeMessage,
        InvocationMessage,
        Message,
    )
    from pysignalr.protocol.json import JSONProtocol, MessageEncoder
    from watchdog.events import FileSystemEvent, FileSystemEventHandler
    from watchdog.observers import Observer
    from watchdog.observers.polling import PollingObserver

    import smartspace.blocks
    import smartspace.cli.auth
    import smartspace.cli.config

    config = smartspace.cli.config.load_config()

    if not config["config_api_url"]:
        print(
            "You must set your API url before creating blocks. Use 'smartspace config --api-url <Your SmartSpace API Url>'"
        )
        exit()

    root_path = path if path != "" else os.getcwd()

    print(f"Debugging blocks in '{root_path}'")

    message_encoder = MessageEncoder()

    class MyJSONProtocol(JSONProtocol):
        def encode(self, message: Message | HandshakeMessage) -> str:
            if isinstance(message, CompletionMessage):
                data = message.dump()
                if "error" in data and data["error"] is None:
                    del data["error"]
                return message_encoder.encode(data)
            else:
                return JSONProtocol.encode(self, message)

    client = SignalRClient(
        url=f"{config['config_api_url']}/debug",
        access_token_factory=smartspace.cli.auth.get_token,
        headers={"Authorization": f"Bearer {smartspace.cli.auth.get_token()}"},
        protocol=MyJSONProtocol(),
    )

    blocks: list[tuple[BlockInterface, type[Block]]] = []

    async def on_message_override(message: Message):
        if isinstance(message, InvocationMessage) and message.target == "run_block":
            request = DebugBlockRequest.model_validate(message.arguments[0])

            print(
                f"Running block {request.block_definition.type.name} ({request.block_definition.type.version})"
            )

            block = first(
                [
                    block_type
                    for block_interface, block_type in blocks
                    if block_interface.name == request.block_definition.type.name
                    and block_interface.version == request.block_definition.type.version
                ]
            )

            outputs: list[FlowValue] = []
            callbacks: list[DebugBlockResult.Callback] = []

            def register_tool_callback(
                tool_id: str,
                tool_call_values: list[FlowValue],
                callback: CallbackCall,
            ):
                callbacks.append(
                    DebugBlockResult.Callback(
                        tool_id=tool_id,
                        tool_call_values=tool_call_values,
                        callback=callback,
                    )
                )

            def emit_output_value(value: Any, source: ValueSourceRef) -> FlowValue:
                flow_value = FlowValue(
                    id=uuid.uuid4(),
                    value_source=source,
                    parent_ids=[parent.id for parent in request.inputs.values()],
                    value=value,
                )
                outputs.append(flow_value)

                return flow_value

            block_instance = block(
                register_tool_callback=register_tool_callback,
                emit_output_value=emit_output_value,
                definition=request.block_definition,
                flow_context=request.flow_context,
            )

            step_instance = block_instance._steps_instances[request.step_id]

            step_kwargs: dict[str, Any] = {
                input_name: value.value for input_name, value in request.inputs.items()
            }

            await step_instance.run(**step_kwargs)

            updated_state = {
                state_name: getattr(block_instance, state_name, None)
                for state_name in request.block_definition.states.keys()
            }

            result = DebugBlockResult(
                states=updated_state,
                outputs=outputs,
                callbacks=callbacks,
            )

            message = CompletionMessage(
                message.invocation_id,
                result.model_dump(by_alias=True, mode="json"),
                headers=client._headers,
            )
            await client._transport.send(message)
        else:
            await SignalRClient._on_message(client, message)

    client._on_message = on_message_override
    client._transport._callback = on_message_override

    async def on_close() -> None:
        print("Disconnected from the server")

    async def on_error(message: CompletionMessage) -> None:
        print(f"Received error: {message.error}")

    async def on_open() -> None:
        await register_blocks(root_path)

    async def register_blocks(path: str):
        found_blocks = [
            (b.interface(version="debug"), b) for b in smartspace.blocks.load(path)
        ]
        new_blocks = [
            b
            for b in found_blocks
            if not any(
                [
                    old_block[0].name == b[0].name
                    and old_block[0].version == b[0].version
                    for old_block in blocks
                ]
            )
        ]

        updated_blocks = [
            b
            for b in found_blocks
            if any(
                [
                    old_block[0].name == b[0].name
                    and old_block[0].version == b[0].version
                    and old_block[0] != b[0]
                    for old_block in blocks
                ]
            )
        ]

        removed_blocks = [
            old_block
            for old_block in blocks
            if not any(
                [
                    old_block[0].name == b[0].name
                    and old_block[0].version == b[0].version
                    for b in found_blocks
                ]
            )
        ]

        for block_interface, _ in updated_blocks:
            print(f"Updating {block_interface.name}")
            data = block_interface.model_dump(by_alias=True, mode="json")
            await client.send("registerblock", [data])

        for block_interface, _ in new_blocks:
            print(f"Registering {block_interface.name}")
            data = block_interface.model_dump(by_alias=True, mode="json")
            await client.send("registerblock", [data])

        for block_interface, _ in removed_blocks:
            print(f"Removing {block_interface.name}")
            data = block_interface.model_dump(by_alias=True, mode="json")
            await client.send("removeblock", [data])

        blocks.clear()
        blocks.extend(found_blocks)

        if not len(blocks):
            print("Found no blocks")

    client.on_open(on_open)
    client.on_close(on_close)
    client.on_error(on_error)

    class _EventHandler(FileSystemEventHandler):
        def __init__(self, loop: asyncio.AbstractEventLoop, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.loop = loop

        def _on_any_event(self, event: FileSystemEvent):
            asyncio.run_coroutine_threadsafe(register_blocks(root_path), self.loop)

        def on_created(self, event: FileSystemEvent):
            self._on_any_event(event)

        def on_deleted(self, event: FileSystemEvent):
            self._on_any_event(event)

        def on_modified(self, event: FileSystemEvent):
            self._on_any_event(event)

        def on_moved(self, event: FileSystemEvent):
            self._on_any_event(event)

    async def main():
        loop = asyncio.get_event_loop()
        handler = _EventHandler(loop)
        observer = PollingObserver() if poll else Observer()
        observer.schedule(handler, root_path, recursive=True)
        observer.start()

        await client.run()

    with suppress(KeyboardInterrupt, asyncio.CancelledError):
        asyncio.run(main())


if __name__ == "__main__":
    debug()
