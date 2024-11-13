import json
from typing import List

import pydantic_core
import requests
import typer
from pydantic import TypeAdapter

from smartspace.cli.models import PublishedBlockSet
from smartspace.core import BlockSet
from smartspace.models import (
    BlockRunData,
)

app = typer.Typer()


def get_config():
    import smartspace.cli.auth
    import smartspace.cli.config

    config = smartspace.cli.config.load_config()

    if not config["config_api_url"]:
        print(
            "You must set your API url before using the CLI. Use 'smartspace config --api-url <Your SmartSpace API Url>'"
        )
        exit()

    return config


@app.command()
def list():
    import smartspace.blocks
    import smartspace.cli.auth

    config = get_config()

    response = requests.get(
        url=f"{config['config_api_url']}/blocksets",
        params={"types": "Custom"},
        headers={"Authorization": f"Bearer {smartspace.cli.auth.get_token()}"},
    )

    if response.status_code == 200:
        type_adapter = TypeAdapter(List[PublishedBlockSet])
        block_sets = type_adapter.validate_json(response.content)
        for block_set in block_sets:
            print(f"{block_set.name}:")
            for block_name, versions in block_set.block_interfaces.items():
                for version in versions.keys():
                    print(f"  {block_name} ({version})")
    else:
        print(f"Error: {response.text}")


@app.command()
def delete(name: str):
    import smartspace.blocks
    import smartspace.cli.auth

    config = get_config()

    response = requests.delete(
        url=f"{config['config_api_url']}/blocksets/{name}",
        headers={"Authorization": f"Bearer {smartspace.cli.auth.get_token()}"},
    )

    if response.status_code >= 200 and response.status_code < 300:
        print("Successfully deleted")
    elif response.status_code == 500:
        print("An internal error occured while trying to delete the block set")
    else:
        result = json.loads(response.content)
        print(result["detail"] if "detail" in result else json.dumps(result, indent=2))


@app.command()
def publish(name: str, path: str = ""):
    import os
    import zipfile

    import smartspace.blocks
    import smartspace.cli.auth

    config = get_config()

    file_name = "blocks.zip"
    if os.path.exists(file_name):
        os.remove(file_name)

    block_set = smartspace.blocks.load(path, force_reload=True)

    print("Publishing the following blocks:")
    for block_name, versions in block_set.all.items():
        for version, block_type in versions.items():
            print(f"{block_name} ({version})")

    zf = zipfile.ZipFile(file_name, "w")
    for dirname, subdirs, files in os.walk(path):
        zf.write(dirname)
        for filename in files:
            zf.write(os.path.join(dirname, filename))
    zf.close()

    with open(file_name, "rb") as f:
        response = requests.post(
            url=f"{config['config_api_url']}/blocksets/{name}",
            headers={"Authorization": f"Bearer {smartspace.cli.auth.get_token()}"},
            files={"file": f},
        )
        if response.status_code == 200:
            print("Published!")
        else:
            print(f"Error: {response.text}")

    if os.path.exists(file_name):
        os.remove(file_name)


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

    config = get_config()

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
        url=f"{config['config_api_url']}debug"
        if config["config_api_url"].endswith("/")
        else f"{config['config_api_url']}/debug",
        headers={"Authorization": f"Bearer {smartspace.cli.auth.get_token()}"},
        protocol=MyJSONProtocol(),
    )

    block_set: BlockSet = BlockSet()

    running = (
        asyncio.Lock()
    )  # temp fix to deal with server issue when running blocks in parallel

    async def on_message_override(message: Message):
        if isinstance(message, InvocationMessage) and message.target == "run_block":
            async with running:
                request = BlockRunData.model_validate(message.arguments[0])

                print(
                    f"Running '{request.name}({request.version}).{request.function}()'"
                )

                block_type = block_set.find(request.name, request.version)

                if not block_type:
                    raise Exception(
                        f"Could not find block with name {request.name} and version {request.version}"
                    )

                block_instance = block_type()

                block_instance._load(
                    context=request.context,
                    state=request.state,
                    inputs=request.inputs,
                    dynamic_ports=request.dynamic_ports,
                    dynamic_output_pins=request.dynamic_output_pins,
                    dynamic_input_pins=request.dynamic_input_pins,
                )

                messages: List[dict] = []

                async for m in await block_instance._run_function(request.function):
                    messages.append(m.model_dump(by_alias=True, mode="json"))

                invocation_id = getattr(message, "invocation_id", None) or getattr(
                    message, "invocationId", ""
                )

                message = CompletionMessage(
                    invocation_id,
                    messages,
                    headers=client._headers,
                )
                print(
                    f"Finished '{request.name}({request.version}).{request.function}()'"
                )
                await client._transport.send(message)
                await asyncio.sleep(5)
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
        nonlocal block_set

        new_block_set = smartspace.blocks.load(path, force_reload=True)
        old_blocks = block_set.all

        found_blocks = {
            block_name: {
                version: block_type.interface()
                for version, block_type in versions.items()
            }
            for block_name, versions in new_block_set.all.items()
        }

        new_blocks = {
            found_block_name: {
                version: block_interface
                for version, block_interface in found_block_versions.items()
                if not any(
                    [
                        old_block_name == found_block_name and version in old_versions
                        for old_block_name, old_versions in old_blocks.items()
                    ]
                )
            }
            for found_block_name, found_block_versions in found_blocks.items()
        }

        removed_blocks = {
            old_block_name: [
                old_version
                for old_version in old_versions.keys()
                if old_block_name not in found_blocks
                or old_version not in found_blocks[old_block_name]
            ]
            for old_block_name, old_versions in old_blocks.items()
        }

        updated_blocks = {
            found_block_name: {
                version: block_interface
                for version, block_interface in found_block_versions.items()
                if any(
                    [
                        old_block_name == found_block_name
                        and version in old_versions
                        and block_interface != old_versions[version].interface()
                        for old_block_name, old_versions in old_blocks.items()
                    ]
                )
            }
            for found_block_name, found_block_versions in found_blocks.items()
        }

        has_updated_blocks = False

        for block_name, versions in updated_blocks.items():
            for version, interface in versions.items():
                has_updated_blocks = True
                print(f"Updating {block_name} ({version})")

        if has_updated_blocks:
            data = pydantic_core.to_jsonable_python(updated_blocks)
            await client.send("registerblock", [data])

        has_new_blocks = False

        for block_name, versions in new_blocks.items():
            for version, interface in versions.items():
                has_new_blocks = True
                print(f"Registering {block_name} ({version})")

        if has_new_blocks:
            data = pydantic_core.to_jsonable_python(new_blocks)
            await client.send("registerblock", [data])

        for block_name, removed_versions in removed_blocks.items():
            for version in removed_versions:
                print(f"Removing {block_name} ({version})")
                await client.send(
                    "removeblock", [{"name": block_name, "version": version}]
                )

        if not len(new_block_set.all):
            print("Found no blocks")

        block_set = new_block_set

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
