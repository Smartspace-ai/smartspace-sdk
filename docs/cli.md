This documentation will help users understand how to use the SmartSpace CLI tool, designed to deploy and debug 'blocks' within a workflow.

## Installation

Use your package manager of choice to install the SmartSpace CLI tool.


`pip` comes standard with Python installations, while `poetry` ([python-poetry.org](https://python-poetry.org/))  is a popular package manager for Python projects but requires a separate installation onto your system.

**pip**
```bash
pip install smartspace-ai
```

**poetry**
```bash
poetry add smartspace-ai
```

Once installed, you can use the `smartspace` command in your terminal to interact with the SmartSpace API.

---

## Configuration

The CLI tool requires configuration settings for interacting with the SmartSpace API. You can configure the tool using the `config` command.

???+ info "Configuration Details"

    You can find the configuration ids in the SmartSpace Admin portal in the "Config API" section.

    ![smartspace side panel showing Config API link](<images/cli/2024-10-11_12-47-54_Arc_Simfony Admin.png>)

    ![smartspace cli setup instructions](<images/cli/2024-10-11_12-48-28_Arc_Simfony Admin.png>)

### Command:
```bash
smartspace config [OPTIONS]
```

### Options:
- `--api-url`: The base URL for the SmartSpace API.
- `--tenant-id`: Your Microsoft Tenant ID.
- `--client-id`: Your SmartSpace Client ID.

Example:
```bash
smartspace config --api-url https://api.smartspace.com --tenant-id your-tenant-id --client-id your-client-id
```

This command updates the configuration file located at `~/.smartspace/config.json`.

---

## Login

To authenticate with SmartSpace, use the `login` command. There are two options for login:

1. Device Code Authentication (recommended for headless environments).
2. Interactive Authentication.

### Command:
```bash
smartspace login [OPTIONS]
```

### Options:
- `--device-code`: If specified, login using a device code flow, prompting the user to authorize the app on another device.

Example:
```bash
smartspace login --device-code
```

If successful, the login command will save the token cache for future interactions.

---

## Blocks Management

The CLI provides tools to publish and debug blocks in your workflow.

### Publishing Blocks

To publish a block, use the `publish` command. This command compresses your blocks into a `.zip` file and uploads them to the SmartSpace API.

### Command:
```bash
smartspace blocks publish [OPTIONS]
```

### Arguments:
- `name`: The name of the block set.
- `path`: The path to the directory containing your blocks (default is the current directory).

Example:
```bash
smartspace blocks publish my_block_set /path/to/blocks
```

This will output the names of the blocks being published and send the ZIP file to the configured API.

---

### Debugging Blocks

To start debugging a block, use the `debug` command. This monitors file changes and synchronizes block registration with the server.

### Command:
```bash
smartspace blocks debug [OPTIONS]
```

### Options:
- `path`: The path to the block directory to debug (default is the current working directory).
- `--poll`: Use a polling observer for file system events (useful for network filesystems).

Example:
```bash
smartspace blocks debug /path/to/blocks
```

This command connects to the SmartSpace server, registers your blocks, and waits for file changes to trigger updates.

---

## Debugging in VS Code

For a more integrated debugging experience, you can use VS Code with a launch configuration for the SmartSpace CLI. This will allow to run a debug session directly from the editor, enabling breakpoints and variable inspection.

### Launch Configuration

Add the following configuration to your `.vscode/launch.json` file (or create one if it doesn't exist):

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Debug Smartspace blocks",
      "type": "debugpy",
      "request": "launch",
      "program": "${workspaceFolder}/venv/bin/smartspace",
      "console": "internalConsole",
      "args": [
        "blocks",
        "debug",
        "--poll",
        "--path",
        "custom_blocks"
      ]
    }
  ]
}
```

This configuration adds a new launch option to your VS Code debugger, allowing you to start a debug session for your SmartSpace blocks.

???+ info "Setting Configuration Values"

    - `program`: The path to the SmartSpace CLI executable.
        - In this example, it assumes the CLI is installed in a virtual environment (`venv`) but if your install location is different, update the path accordingly.
    - `args`: The arguments to pass to the CLI for debugging blocks.
        - `--poll`: Use a polling observer for changes in the block files, so the CLI can detect updates.
        - `--path`: The path to the block directory to debug.
            - in this example, it assumes the blocks are located in a directory named `custom_blocks`, but you should replace this with the actual path to your block files.

![vs code debug option](<images/cli/2024-10-11_12-58-08_Visual Studio Code - Insiders_cli.md — workspace [Dev Container SmartSpace Flows @ desktop-linux].png>)

In the "Run and Debug" panel, select the "Debug Smartspace blocks" configuration and then click the run button to start debugging your blocks. This will connect to the connected SmartSpace environment and monitor your block files for changes. You can now run a workflow back in SmartSpace that includes your custom block(s) and debug them directly from VS Code. When a breakpoint is hit in the custom block, it will pause execution and allow you to inspect variables and general state. Any changes you make to your block files will be automatically updated in the SmartSpace environment.

## Utilities

### Configuration Management

The configuration is stored locally in a JSON file. Use the `config` command to set or update your configuration details, such as API URLs, client IDs, and tenant IDs. The configuration file is located at:

```
~/.smartspace/config.json
```

Use the `config` command (as described [here](#configuration)) to manage these settings.

---

## Example Workflow

1. **Configure the CLI** with the API URL, tenant ID, and client ID:
   ```bash
   smartspace config --api-url https://api.smartspace.com --tenant-id your-tenant-id --client-id your-client-id
   ```

2. **Login** to the CLI:
   ```bash
   smartspace login --device-code
   ```

3. **Publish your blocks**:
   ```bash
   smartspace blocks publish my_block_set /path/to/blocks
   ```

4. **Debug your blocks** during development:
   ```bash
   smartspace blocks debug /path/to/blocks
   ```

---

## Error Handling

- If you encounter missing configuration errors while trying to publish or debug, ensure that the API URL, client ID, and tenant ID are correctly set using the `config` command.
- If authentication fails, retry the login command or verify the client ID and tenant ID in the configuration.