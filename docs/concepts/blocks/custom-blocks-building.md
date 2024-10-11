This guide will walk you through the steps of creating new blocks for the SmartSpace platform using the provided core block framework. Blocks are reusable components that perform specific tasks in workflows and can be configured with various inputs, outputs, and states.

---

## Block Structure

Blocks are Python classes that inherit from the `Block` base class and optionally from other generic types to support various input and output types. Each block should:

  - Contain inputs and outputs as typed attributes.
  - Implement logic in **steps** or **callbacks**.
  - Optionally use **states** to store intermediate or persistent values.
  - Provide metadata for categorisation and description.

---

## Creating a Simple Block

To create a new block, define a class that extends `Block` and optionally a generic type if needed. You can define the block’s inputs, outputs, and internal logic within the class.

### Example:
```python
from smartspace.core import Block, step

class Count(Block):
    @step(output_name="output")
    async def count(self, items: list[Any]) -> int:
        return len(items)
```

In this example, the `Count` block takes a list of items and outputs the count.

---

## Adding Metadata

You can add metadata to a block to provide descriptive information such as the block’s category, description, or other attributes that are important for its usage in the SmartSpace system. Use the `@metadata` decorator for this purpose.

### Example:
```python
from smartspace.core import Block, metadata, step
from smartspace.enums import BlockCategory

@metadata(
    category=BlockCategory.FUNCTION,
    description="Counts the number of items in a list."
)
class Count(Block):
    @step(output_name="output")
    async def count(self, items: list[Any]) -> int:
        return len(items)
```

The `@metadata` decorator adds useful information for developers and users of the block.

---

## Working with Input and Output Pins

Blocks interact with other blocks via **input** and **output** pins. These pins can be single values, lists, or dictionaries. You can define inputs and outputs using Python type annotations.

### Defining Inputs:
```python
from smartspace.core import Block, step

class Count(Block):
    @step(output_name="output")
    async def count(self, items: list[Any]) -> int:
        return len(items)
```
Here, the `items` parameter is the input, which is a list of any type.

### Defining Outputs:
Outputs are defined similarly to inputs but are typically sent using the `send` method.
```python
class Sum(Block):
    total: Output[int]

    @step()
    async def sum(self, items: list[int]):
        self.total.send(sum(items))
```

---

## Working with States

States in SmartSpace blocks store values that persist across the execution of the block. You can define state variables using the `State` annotation.

### Example:
```python
from typing import Annotated
from smartspace.core import Block, step, State

class Accumulator(Block):
    total: Annotated[int, State(step_id="accumulate", input_ids=["items"])] = 0

    @step()
    async def accumulate(self, items: list[int]):
        self.total += sum(items)
```

In this example, the `total` variable persists across multiple calls to the `accumulate` method.

---

## Defining Block Functions

You can define block functions using the `@step` and `@callback` decorators. Steps are core functions of the block, while callbacks are executed in response to specific events.

### Defining a Step:
```python
class Multiply(Block):
    @step(output_name="result")
    async def multiply(self, x: int, y: int) -> int:
        return x * y
```
Steps are async functions that execute the main logic of the block.

### Defining a Callback:
```python
class MultiplyAndStore(Block):
    @step()
    async def multiply(self, x: int, y: int):
        result = x * y
        await self.store_result(result)

    @callback()
    async def store_result(self, result: int):
        print(f"Result: {result}")
```
Callbacks allow you to define actions that respond to the results of other steps or tools.

---

## Handling Dynamic Inputs and Outputs

In some cases, blocks may need to dynamically handle inputs and outputs at runtime. For example, a block could process a variable number of inputs or outputs. You can define dynamic ports using lists or dictionaries of inputs and outputs.

### Example:
```python
class DynamicBlock(Block):
    dynamic_inputs: list[Input[int]]
    dynamic_outputs: dict[str, Output[int]]

    @step()
    async def process(self):
        for input_value in self.dynamic_inputs:
            output_value = input_value * 2
            self.dynamic_outputs[str(input_value)].send(output_value)
```

---

## Examples

### Example: Map Block
The `Map` block applies a tool to each item in a list and collects the results.

```python
from smartspace.core import Block, Tool, Output, step, callback

class Map(Block):
    class Operation(Tool):
        def run(self, item: int) -> int:
            return item * 2

    results: Output[list[int]]

    @step()
    async def map(self, items: list[int]):
        self.results.send([self.run.call(item) for item in items])
```

### Example: Collect Block
The `Collect` block collects data from a channel and outputs it once the channel closes.

```python
from smartspace.core import Block, InputChannel, Output, step

class Collect(Block):
    items: Output[list[int]]

    @step()
    async def collect(self, item: InputChannel[int]):
        items = []
        while not item.closed:
            data = await item.receive()
            items.append(data)

        self.items.send(items)
```

---

## Available Python Libraries

Currently (as of October 2024), SmartSpace supports the following Python libraries for use in blocks:

```
aiohappyeyeballs==2.4.3
aiohttp==3.10.8
aiosignal==1.3.1
annotated-types==0.5.0
antlr4-python3-runtime==4.9.3
anyio==3.7.1
asgiref==3.8.1
async-timeout==4.0.3
attrs==24.2.0
azure-common==1.1.28
azure-core==1.31.0
azure-cosmos==4.7.0
azure-identity==1.17.1
azure-monitor-opentelemetry-exporter==1.0.0b19
azure-search-documents==11.4.0a20230509004
azure-storage-blob==12.19.0
azure-storage-queue==12.9.0
backoff==2.2.1
beautifulsoup4==4.12.3
build==1.2.2
CacheControl==0.14.0
cachetools==5.5.0
certifi==2023.7.22
cffi==1.17.1
chardet==5.2.0
charset-normalizer==3.3.2
cleo==2.1.0
click==8.1.7
coloredlogs==15.0.1
contourpy==1.3.0
coverage==7.6.1
crashtest==0.4.1
cryptography==43.0.1
cycler==0.12.1
dataclasses-json==0.6.7
Deprecated==1.2.14
dirtyjson==1.0.8
distlib==0.3.8
distro==1.9.0
dnspython==2.4.2
docx2txt==0.8
dulwich==0.21.7
effdet==0.4.1
email-validator==2.0.0.post2
emoji==2.13.2
et-xmlfile==1.1.0
exceptiongroup==1.1.3
fastapi==0.101.1
fastapi-injector==0.5.1
fastjsonschema==2.20.0
filelock==3.16.1
filetype==1.2.0
fixedint==0.1.6
flatbuffers==24.3.25
fonttools==4.54.1
frozenlist==1.4.1
fsspec==2024.9.0
google-ai-generativelanguage==0.6.1
google-api-core==2.20.0
google-api-python-client==2.147.0
google-auth==2.35.0
google-auth-httplib2==0.2.0
google-generativeai==0.5.0
googleapis-common-protos==1.65.0
greenlet==3.1.1
grpcio==1.66.2
grpcio-status==1.62.3
grpcio-tools==1.62.3
h11==0.14.0
h2==4.1.0
hpack==4.0.0
httpcore==1.0.6
httplib2==0.22.0
httptools==0.6.0
httpx==0.27.2
httpx-sse==0.4.0
huggingface-hub==0.25.1
humanfriendly==10.0
hyperframe==6.0.1
idna==3.4
importlib-metadata==6.11.0
iniconfig==2.0.0
injector==0.21.0
installer==0.7.0
iopath==0.1.10
isodate==0.6.1
itsdangerous==2.1.2
jaraco.classes==3.4.0
jeepney==0.8.0
Jinja2==3.1.2
jiter==0.5.0
joblib==1.4.2
jsonpath-ng==1.6.1
jsonschema==4.23.0
jsonschema-specifications==2023.12.1
keyring==24.3.1
kiwisolver==1.4.7
langdetect==1.0.9
layoutparser==0.3.4
litellm==1.48.9
llama-cloud==0.1.0
llama-index==0.11.15
llama-index-agent-openai==0.3.4
llama-index-cli==0.3.1
llama-index-core==0.11.15
llama-index-embeddings-huggingface==0.3.1
llama-index-embeddings-openai==0.2.5
llama-index-indices-managed-llama-cloud==0.4.0
llama-index-legacy==0.9.48.post3
llama-index-llms-openai==0.2.10
llama-index-multi-modal-llms-openai==0.2.1
llama-index-program-openai==0.2.0
llama-index-question-gen-openai==0.2.0
llama-index-readers-file==0.2.2
llama-index-readers-llama-parse==0.3.0
llama-parse==0.5.6
lxml==5.3.0
markdown-it-py==3.0.0
MarkupSafe==2.1.3
marshmallow==3.22.0
matplotlib==3.9.2
mdurl==0.1.2
minijinja==2.2.0
more-itertools==10.5.0
motor==3.6.0
mpmath==1.3.0
msal==1.31.0
msal-extensions==1.2.0
msgpack==1.1.0
msrest==0.7.1
multidict==6.1.0
mypy==1.11.2
mypy-extensions==1.0.0
neo4j==5.25.0
nest-asyncio==1.6.0
networkx==3.3
nltk==3.9.1
numpy==1.26.4
oauthlib==3.2.2
omegaconf==2.3.0
onnx==1.17.0
onnxruntime==1.15.1
openai==1.51.0
opencv-python==4.10.0.84
openpyxl==3.1.2
opentelemetry-api==1.21.0
opentelemetry-instrumentation==0.42b0
opentelemetry-instrumentation-asgi==0.42b0
opentelemetry-instrumentation-fastapi==0.42b0
opentelemetry-instrumentation-logging==0.42b0
opentelemetry-instrumentation-requests==0.42b0
opentelemetry-instrumentation-system-metrics==0.42b0
opentelemetry-sdk==1.21.0
opentelemetry-semantic-conventions==0.42b0
opentelemetry-util-http==0.42b0
orjson==3.9.5
packaging==24.1
pandas==2.2.3
pandas-stubs==2.2.2.240909
pdf2image==1.17.0
pdfminer.six==20231228
pdfplumber==0.11.4
pexpect==4.9.0
pillow==10.4.0
pkginfo==1.11.1
platformdirs==4.3.6
pluggy==1.5.0
ply==3.11
poetry==1.8.2
poetry-core==1.9.0
poetry-plugin-export==1.8.0
portalocker==2.10.1
proto-plus==1.24.0
protobuf==4.25.5
psutil==5.9.8
ptyprocess==0.7.0
pyasn1==0.6.1
pyasn1_modules==0.4.1
pycocotools==2.0.8
pycparser==2.22
pydantic==2.7.0
pydantic-extra-types==2.0.0
pydantic-settings==2.0.3
pydantic_core==2.18.1
Pygments==2.18.0
PyJWT==2.9.0
pymongo==4.9.2
pypandoc==1.13
pyparsing==3.1.4
pypdf==4.3.1
PyPDF2==3.0.1
pypdfium2==4.30.0
pyproject_hooks==1.2.0
pysignalr==1.0.0
pytesseract==0.3.13
pytest==8.3.3
pytest-asyncio==0.23.8
pytest-cov==4.1.0
pytest-mock==3.14.0
python-dateutil==2.9.0.post0
python-docx==1.1.2
python-dotenv==1.0.1
python-iso639==2024.4.27
python-magic==0.4.27
python-multipart==0.0.6
pytz==2024.2
PyYAML==6.0.1
qdrant-client==1.11.3
RapidFuzz==3.10.0
referencing==0.35.1
regex==2024.9.11
requests==2.32.3
requests-oauthlib==2.0.0
requests-toolbelt==1.0.0
rich==13.9.1
rpds-py==0.20.0
rsa==4.9
ruff==0.3.7
safetensors==0.4.5
scikit-learn==1.5.2
scipy==1.14.1
SecretStorage==3.3.3
semantic-version==2.10.0
sentence-transformers==3.1.1
shellingham==1.5.4
six==1.16.0
sniffio==1.3.0
soupsieve==2.6
SQLAlchemy==2.0.35
sse-starlette==2.1.3
starlette==0.27.0
striprtf==0.0.26
sympy==1.13.3
tabulate==0.9.0
tenacity==8.2.3
threadpoolctl==3.5.0
tiktoken==0.7.0
timm==1.0.9
tokenizers==0.20.0
tomli==2.0.1
tomlkit==0.13.2
torch==2.4.1
torchvision==0.19.1
tqdm==4.66.5
transformers==4.45.1
trove-classifiers==2024.9.12
typer==0.12.5
types-jsonschema==4.23.0.20240813
types-openpyxl==3.1.5.20240918
types-pytz==2024.2.0.20240913
types-PyYAML==6.0.12.20240917
types-regex==2023.12.25.20240311
types-requests==2.32.0.20240914
typing-inspect==0.9.0
typing_extensions==4.12.2
tzdata==2024.2
ujson==5.8.0
unstructured==0.10.27
unstructured-inference==0.7.10
unstructured.pytesseract==0.3.13
uritemplate==4.1.1
urllib3==2.2.3
uvicorn==0.23.2
uvloop==0.17.0
virtualenv==20.26.6
watchdog==4.0.1
watchfiles==0.19.0
websockets==12.0
wrapt==1.16.0
yarl==1.13.1
zipp==3.20.2
```

In future versions, SmartSpace will enable the use of any Python library as the custom blocks will be running in a secure and isolated environment.

---

## Conclusion

Blocks in SmartSpace are highly customizable and can be tailored to perform specific tasks within workflows. By following the examples above, you can create new blocks to expand the functionality of the SmartSpace platform. Remember to define inputs, outputs, and states clearly, and use the appropriate decorators (`@step`, `@callback`, `@metadata`) to create powerful and reusable components.