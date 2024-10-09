def login(deviceCode: bool):
    import json

    import msal

    msal_app = get_msal_app()

    config = _get_config()
    scope = f"api://{config['client_id']}/smartspaceapi.config.access"

    accounts = msal_app.get_accounts()
    for account in accounts:
        msal_app.remove_account(account)

    if deviceCode:
        flow = msal_app.initiate_device_flow(
            scopes=[scope],
        )

        if "user_code" not in flow:
            raise ValueError(
                "Fail to create device flow. Err: %s" % json.dumps(flow, indent=4)
            )

        print(flow["message"])

        result = msal_app.acquire_token_by_device_flow(
            flow=flow,
        )

    else:
        result = msal_app.acquire_token_interactive(
            scopes=[scope],
            prompt=msal.Prompt.SELECT_ACCOUNT,
        )

    if "error" in result:
        if "error_description" in result:
            print(f"Login failed with error: '{result['error_description']}'")
        else:
            print(f"Login failed with error: '{result['error']}'")
    else:
        print("Logged in successfully")


def get_msal_app():
    import atexit
    import os

    import msal

    config = _get_config()

    cache_filename = os.path.join(
        os.getenv("XDG_RUNTIME_DIR", os.path.expanduser("~")),
        ".smartspace",
        "msal_token_cache",
    )
    cache = msal.SerializableTokenCache()
    if os.path.exists(cache_filename):
        cache.deserialize(open(cache_filename, "r").read())

    atexit.register(
        lambda: open(cache_filename, "w").write(cache.serialize())
        if cache.has_state_changed
        else None
    )

    return msal.PublicClientApplication(
        client_id=config["client_id"],
        authority=f"https://login.microsoftonline.com/{config['tenant_id']}",
        token_cache=cache,
    )


def get_token() -> str:
    config = _get_config()
    msal_app = get_msal_app()
    accounts = msal_app.get_accounts()

    if len(accounts) == 0:
        print("You are not logged in. Please run 'smartspace login'")
        exit()

    token = msal_app.acquire_token_silent(
        scopes=[f"api://{config['client_id']}/smartspaceapi.config.access"],
        account=accounts[0],
    )

    if token is None or "access_token" not in token:
        print("You are not logged in. Please run 'smartspace login'")
        exit()

    return token["access_token"]


def _get_config():
    import smartspace.cli.config

    config = smartspace.cli.config.load_config()
    if not config["client_id"] and config["tenant_id"]:
        print(
            "You must set your client ID before logging in. Use 'smartspace config --client-id <Your SmartSpace Client ID>'"
        )
        exit()

    if config["client_id"] and not config["tenant_id"]:
        print(
            "You must set your tenant ID before logging in. Use 'smartspace config --tenant-id <Your Microsoft Tenant ID>'"
        )
        exit()

    if not config["client_id"] and not config["tenant_id"]:
        print(
            "You must set your tenant ID and client ID before logging in. Use 'smartspace config --tenant-id <Your Microsoft Tenant ID>' --client-id <Your SmartSpace Client ID>"
        )
        exit()

    return config
