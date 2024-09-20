import json
from typing import Annotated, Optional

import typer

from smartspace.cli import blocks
from smartspace.cli.config import SmartSpaceConfig

app = typer.Typer()
app.add_typer(blocks.app, name="blocks")


@app.command()
def config(
    apiUrl: Annotated[Optional[str], typer.Option("--api-url")] = None,
    tenantId: Annotated[Optional[str], typer.Option("--tenant-id")] = None,
    clientId: Annotated[Optional[str], typer.Option("--client-id")] = None,
):
    from smartspace.cli.config import load_config, save_config

    current_config = load_config()
    new_config = SmartSpaceConfig(
        config_api_url=current_config["config_api_url"] if apiUrl is None else apiUrl,
        tenant_id=current_config["tenant_id"] if tenantId is None else tenantId,
        client_id=current_config["client_id"] if clientId is None else clientId,
    )

    if apiUrl or tenantId or clientId:
        save_config(new_config)
        print("Config updated")

    print(json.dumps(new_config, indent=2))


@app.command()
def login(deviceCode: Annotated[bool, typer.Option("--device-code")] = False):
    from smartspace.cli import auth

    auth.login(deviceCode=deviceCode)


def cli():
    app()


if __name__ == "__main__":
    cli()
