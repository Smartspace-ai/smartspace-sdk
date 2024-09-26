This documentation will help users understand how to use the SmartSpace CLI tool, designed to deploy and debug 'blocks' within a workflow.

## 1. Installation

Ensure you have `typer`, `msal`, `requests`, `watchdog`, and `pysignalr` installed. If not, install them via:

```bash
pip install typer msal requests watchdog pysignalr
```

Once the dependencies are installed, clone or download the repository and run the tool from the terminal.

---

## 2. Configuration

The CLI tool requires configuration settings for interacting with the SmartSpace API. You can configure the tool using the `config` command.

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

## 3. Login

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

## 4. Blocks Management

The CLI provides tools to publish and debug blocks in your workflow.

### 4.1. Publishing Blocks

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

### 4.2. Debugging Blocks

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

## 5. Utilities

### 5.1. Configuration Management

The configuration is stored locally in a JSON file. Use the `config` command to set or update your configuration details, such as API URLs, client IDs, and tenant IDs. The configuration file is located at:

```
~/.smartspace/config.json
```

Use the `config` command (as described in Section 2) to manage these settings.

---

## 6. Example Workflow

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

## 7. Error Handling

- If you encounter missing configuration errors while trying to publish or debug, ensure that the API URL, client ID, and tenant ID are correctly set using the `config` command.
- If authentication fails, retry the login command or verify the client ID and tenant ID in the configuration.