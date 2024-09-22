from typing import TypedDict


class SmartSpaceConfig(TypedDict):
    client_id: str | None
    tenant_id: str | None
    config_api_url: str | None


def load_config() -> SmartSpaceConfig:
    import json

    try:
        with open(_get_config_file_path(), "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return SmartSpaceConfig(client_id=None, config_api_url=None, tenant_id=None)


def save_config(config: SmartSpaceConfig):
    import json
    import os
    from pathlib import Path

    Path(os.path.join(os.path.expanduser("~"), ".smartspace")).mkdir(
        parents=True, exist_ok=True
    )

    with open(_get_config_file_path(), "w+") as f:
        json.dump(config, f)


def _get_config_file_path():
    import os

    home_directory = os.path.expanduser("~")
    return os.path.join(home_directory, ".smartspace", "config.json")
