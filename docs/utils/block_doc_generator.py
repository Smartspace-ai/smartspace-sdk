import ast
import logging
import os
import sys
from typing import Any, TypedDict, cast

logging.basicConfig(level=logging.DEBUG, filename="block_doc_generator.log")
logger = logging.getLogger(__name__)


def parse_module(file_path):
    with open(file_path, "r") as file:
        module_source = file.read()
    module_ast = ast.parse(module_source, filename=file_path)
    return module_ast


def get_block_classes(module_ast) -> list[ast.ClassDef]:
    block_classes: list[ast.ClassDef] = []
    for node in module_ast.body:
        if isinstance(node, ast.ClassDef):
            for base in node.bases:
                if (isinstance(base, ast.Name) and base.id == "Block") or (
                    isinstance(base, ast.Attribute) and base.attr == "Block"
                ):
                    block_classes.append(node)
    return block_classes


def get_block_class(block_name: str) -> ast.ClassDef | None:
    files = [
        os.path.join("smartspace/blocks", f)
        for f in os.listdir("smartspace/blocks")
        if f.endswith(".py")
    ]
    for file_path in files:
        module_ast = parse_module(file_path)
        block_classes = get_block_classes(module_ast)
        for class_info in block_classes:
            if class_info.name == block_name:
                return class_info


def get_value_from_node(node):
    if isinstance(node, ast.Constant):  # For literals like strings, numbers, etc.
        return node.value
    elif isinstance(node, ast.Str):  # For Python versions < 3.8
        return node.s
    elif isinstance(node, ast.Num):  # For Python versions < 3.8
        return node.n
    elif isinstance(node, ast.Name):
        return node.id
    elif isinstance(node, ast.Attribute):
        value = get_value_from_node(node.value)
        return f"{value}.{node.attr}"
    elif isinstance(node, ast.Call):
        func_name = get_value_from_node(node.func)
        args = [get_value_from_node(arg) for arg in node.args]
        keywords = {kw.arg: get_value_from_node(kw.value) for kw in node.keywords}
        return {"func": func_name, "args": args, "keywords": keywords}
    elif isinstance(node, ast.List):
        return [get_value_from_node(el) for el in node.elts]
    elif isinstance(node, ast.Tuple):
        return tuple(get_value_from_node(el) for el in node.elts)
    elif isinstance(node, ast.Dict):
        keys = [get_value_from_node(k) for k in node.keys]
        values = [get_value_from_node(v) for v in node.values]
        return dict(zip(keys, values))
    elif isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        # Handle negative numbers
        return -get_value_from_node(node.operand)
    elif isinstance(node, ast.BinOp):
        left = get_value_from_node(node.left)
        right = get_value_from_node(node.right)
        if isinstance(node.op, ast.Add):
            return left + right
        elif isinstance(node.op, ast.Sub):
            return left - right
        elif isinstance(node.op, ast.Mult):
            return left * right
        elif isinstance(node.op, ast.Div):
            return left / right
        else:
            return f"Unsupported BinOp({ast.dump(node.op)})"
    elif isinstance(
        node, ast.NameConstant
    ):  # For True, False, None in Python versions < 3.8
        return node.value
    else:
        return ast.dump(node)  # For debugging purposes or unhandled cases


def get_annotation_name(annotation_node):
    if isinstance(annotation_node, ast.Name):
        return annotation_node.id
    elif isinstance(annotation_node, ast.Subscript):
        base = get_annotation_name(annotation_node.value)
        sub = get_annotation_name(annotation_node.slice)
        return f"{base}[{sub}]"
    elif isinstance(annotation_node, ast.Attribute):
        return f"{get_annotation_name(annotation_node.value)}.{annotation_node.attr}"
    elif isinstance(annotation_node, ast.BinOp):
        if isinstance(annotation_node.op, ast.BitOr):
            left = get_annotation_name(annotation_node.left)
            right = get_annotation_name(annotation_node.right)
            return f"{left} | {right}"
        elif isinstance(annotation_node.op, ast.Add):
            left = get_annotation_name(annotation_node.left)
            right = get_annotation_name(annotation_node.right)
            return f"{left} + {right}"
        elif isinstance(annotation_node.op, ast.Sub):
            left = get_annotation_name(annotation_node.left)
            right = get_annotation_name(annotation_node.right)
            return f"{left} - {right}"
        else:
            return f"Unsupported BinOp({ast.dump(annotation_node.op)})"
    elif isinstance(annotation_node, ast.Tuple):
        elements = [get_annotation_name(el) for el in annotation_node.elts]
        return f"({', '.join(elements)})"
    elif isinstance(annotation_node, ast.Call):
        func_name = get_annotation_name(annotation_node.func)
        args = [get_annotation_name(arg) for arg in annotation_node.args]
        return f"{func_name}({', '.join(args)})"
    else:
        return ast.dump(annotation_node)  # For debugging purposes


class BlockMetadata(TypedDict, total=False):
    category: str
    description: str
    obsolete: bool


def clean_metadata_value(value: Any) -> str:
    if isinstance(value, str) and "BlockCategory" in value:
        value = value.replace("BlockCategory.", "").title()
    return value


def get_metadata_decorator(class_def) -> BlockMetadata:
    metadata_info: BlockMetadata = {}
    for decorator in class_def.decorator_list:
        if isinstance(decorator, ast.Call) and (
            getattr(decorator.func, "id", "") == "metadata"
            or getattr(decorator.func, "attr", "") == "metadata"
        ):
            for keyword in decorator.keywords:
                key = keyword.arg
                if not key:
                    continue
                value = get_value_from_node(keyword.value)
                value = clean_metadata_value(value)
                metadata_info[key] = value
    return metadata_info


def get_subscript_slice_elements(subscript_node):
    if isinstance(subscript_node.slice, ast.Tuple):
        # Python 3.9+, the slice is directly the tuple
        return subscript_node.slice.elts
    elif isinstance(subscript_node.slice, ast.Index):
        # Python <3.9, the value is in slice.value
        value = subscript_node.slice.value
        if isinstance(value, ast.Tuple):
            return value.elts
        else:
            return [value]
    else:
        # In some cases, slice might be an expression directly
        return [subscript_node.slice]


class BlockAttributes(TypedDict, total=False):
    name: str
    type: str | None
    config: bool
    output: bool
    state: bool
    metadata: dict[str, Any] | None
    default_value: Any | None


def get_class_attributes(class_def) -> list[BlockAttributes]:
    attributes: list[BlockAttributes] = []
    for node in class_def.body:
        if isinstance(node, ast.AnnAssign):
            if isinstance(node.target, ast.Name):
                attr_name = node.target.id
            else:
                continue  # Skip if target is not a simple name
            attr_annotation = node.annotation
            attr_info = {
                "name": attr_name,
                "type": None,
                "config": False,
                "output": False,
                "state": False,
                "metadata": None,
                "default_value": None,
            }

            # Process the annotation to extract type and metadata
            if (
                isinstance(attr_annotation, ast.Subscript)
                and get_annotation_name(attr_annotation.value) == "Annotated"
            ):
                # It's an Annotated type
                annotated_args = get_subscript_slice_elements(attr_annotation)
                attr_type = annotated_args[0]
                metadata_node = annotated_args[1] if len(annotated_args) > 1 else None

                attr_info["type"] = get_annotation_name(attr_type)

                # Check if metadata_node is Config, Metadata, or State
                if isinstance(metadata_node, ast.Call):
                    func_name = get_annotation_name(metadata_node.func)
                    if func_name == "Config":
                        attr_info["config"] = True
                        # Extract any Config parameters if needed
                    elif func_name == "Metadata":
                        # Extract metadata details
                        metadata_details = {}
                        for keyword in metadata_node.keywords:
                            key = keyword.arg
                            value = get_value_from_node(keyword.value)
                            metadata_details[key] = value
                        attr_info["metadata"] = metadata_details
                    elif func_name == "State":
                        attr_info["state"] = True
                        # Extract state details if needed
                        state_details = {}
                        for keyword in metadata_node.keywords:
                            key = keyword.arg
                            value = get_value_from_node(keyword.value)
                            state_details[key] = value
                        attr_info["state_details"] = state_details
                else:
                    # Handle cases where metadata_node is not a call (e.g., just a type)
                    pass
            else:
                # Non-Annotated attribute
                attr_info["type"] = get_annotation_name(attr_annotation)

            # Check if the type is 'Output' or 'Output[...]'
            if attr_info["type"].startswith("Output"):
                attr_info["output"] = True

            # Extract default value if available
            if node.value:
                attr_info["default_value"] = get_value_from_node(node.value)

            attributes.append(attr_info)
    return attributes


class BlockStepInput(TypedDict, total=False):
    name: str
    type: str | None
    metadata: dict[str, Any] | None


class BlockStep(TypedDict, total=False):
    name: str
    output_name: str | None
    inputs: list[BlockStepInput]
    return_type: str | None


def get_step_functions(class_def) -> list[BlockStep]:
    steps: list[BlockStep] = []
    for node in class_def.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            is_step = False
            output_name = None
            for decorator in node.decorator_list:
                # Check if decorator is @step or @step(...)
                decorator_name = get_decorator_name(decorator)
                if decorator_name == "step":
                    is_step = True
                    # If it's a call, extract output_name
                    if isinstance(decorator, ast.Call):
                        for keyword in decorator.keywords:
                            if keyword.arg == "output_name":
                                output_name = cast(
                                    str, get_value_from_node(keyword.value)
                                )
            if is_step:
                step_info: BlockStep = {
                    "name": node.name,
                    "output_name": output_name,
                    "inputs": [],
                    "return_type": None,
                }

                # Get inputs (parameters)
                for arg in node.args.args[1:]:  # Skip 'self'
                    input_info: BlockStepInput = {
                        "name": arg.arg,
                        "type": None,
                        "metadata": None,
                    }
                    if arg.annotation:
                        input_info["type"] = get_annotation_name(arg.annotation)
                        # Check if it's Annotated
                        if (
                            isinstance(arg.annotation, ast.Subscript)
                            and get_annotation_name(arg.annotation.value) == "Annotated"
                        ):
                            annotated_args = get_subscript_slice_elements(
                                arg.annotation
                            )
                            input_type = annotated_args[0]
                            metadata_node = (
                                annotated_args[1] if len(annotated_args) > 1 else None
                            )
                            input_info["type"] = get_annotation_name(input_type)

                            # Extract metadata
                            if (
                                isinstance(metadata_node, ast.Call)
                                and get_annotation_name(metadata_node.func)
                                == "Metadata"
                            ):
                                metadata_details = {}
                                for keyword in metadata_node.keywords:
                                    key = keyword.arg
                                    value = get_value_from_node(keyword.value)
                                    metadata_details[key] = value
                                input_info["metadata"] = metadata_details
                    step_info["inputs"].append(input_info)

                # Get return type
                if node.returns:
                    step_info["return_type"] = get_annotation_name(node.returns)

                steps.append(step_info)
    return steps


def get_decorator_name(decorator):
    if isinstance(decorator, ast.Name):
        return decorator.id
    elif isinstance(decorator, ast.Attribute):
        return decorator.attr
    elif isinstance(decorator, ast.Call):
        return get_decorator_name(decorator.func)
    else:
        return None


class BlockInfo(TypedDict):
    name: str
    metadata: BlockMetadata
    attributes: list[BlockAttributes]
    steps: list[BlockStep]


def get_block_info(class_def) -> BlockInfo:
    block_info: BlockInfo = {
        "name": class_def.name,
        "metadata": get_metadata_decorator(class_def),
        "attributes": get_class_attributes(class_def),
        "steps": get_step_functions(class_def),
    }
    return block_info


####
def get_block_markdown_template() -> str:
    with open(os.path.join("docs", "block-reference", "BLOCK-TEMPLATE.md"), "r") as f:
        return f.read()


def generate_block_docs(input_path: str, output_dir: str):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    if os.path.isfile(input_path):
        files = [input_path]
    elif os.path.isdir(input_path):
        files = [
            os.path.join(input_path, f)
            for f in os.listdir(input_path)
            if f.endswith(".py")
        ]
    else:
        raise ValueError("Input path must be a file or directory")

    for file_path in files:
        module = parse_module(file_path)
        block_classes = get_block_classes(module)
        for block_class in block_classes:
            block_info = get_block_info(block_class)
            # check if file already exists
            if os.path.exists(os.path.join(output_dir, f"{block_info['name']}.md")):
                print(f"Documentation for {block_info['name']} already exists")
                continue
            markdown_content = get_block_markdown_template()
            output_file = os.path.join(output_dir, f"{block_info['name']}.md")
            with open(output_file, "w") as f:
                f.write(markdown_content)
            print(f"Generated documentation for {block_info['name']} in {output_file}")


def escape_markdown(text):
    """
    Escapes markdown special characters in the given text.
    """
    if not isinstance(text, str):
        text = str(text)
    # Escape the pipe character
    text = text.replace("|", "or")
    # Escape backsplash
    text = text.replace("\n", "\\n")
    # Clean up HTTPMethod
    text = text.replace("HTTPMethod.", "")

    return text


def generate_markdown(block_info):
    md = ""

    # Block Description
    md += "## Description\n\n"
    description = block_info["metadata"].get("description", "")
    # remove leading and trailing whitespaces for each line
    description = "\n".join([line.strip() for line in description.split("\n")])
    md += f"{description}\n\n"

    # Additional Metadata
    metadata_items = {
        k: v for k, v in block_info["metadata"].items() if k != "description"
    }
    if metadata_items:
        md += "## Metadata\n\n"
        for key, value in metadata_items.items():
            md += f"- **{key.capitalize()}**: {value}\n"
        md += "\n"

    # Config Options
    config_attributes = [attr for attr in block_info["attributes"] if attr["config"]]
    md += "## Configuration Options\n\n"
    if config_attributes:
        md += "| Name | Data Type | Description | Default Value |\n"
        md += "|------|-----------|-------------|---------------|\n"
        for config in config_attributes:
            name = escape_markdown(config["name"])
            data_type = escape_markdown(config["type"])
            description = escape_markdown(
                config["metadata"].get("description", "") if config["metadata"] else ""
            )
            default_value = (
                config["default_value"] if config["default_value"] is not None else ""
            )
            default_value = escape_markdown(default_value)
            md += f"| {name} | `{data_type}` | {description} | {f'`{default_value}`' if default_value else ''} |\n"
    else:
        md += "No configuration options available.\n"
    md += "\n"

    # Inputs
    md += "## Inputs\n\n"
    inputs = []
    for step in block_info["steps"]:
        for input_param in step["inputs"]:
            inputs.append(input_param)
    if inputs:
        md += "| Name | Data Type | Description |\n"
        md += "|------|-----------|-------------|\n"
        for input_param in inputs:
            name = escape_markdown(input_param["name"])
            data_type = escape_markdown(input_param["type"])
            description = escape_markdown(
                input_param["metadata"].get("description", "")
                if input_param["metadata"]
                else ""
            )
            md += f"| {name} | `{data_type}` | {description} |\n"
    else:
        md += "No inputs available.\n"
    md += "\n"

    # Outputs
    md += "## Outputs\n\n"
    outputs = []

    # Outputs from class attributes
    output_attributes = [attr for attr in block_info["attributes"] if attr["output"]]
    for output_attr in output_attributes:
        outputs.append(
            {
                "name": output_attr["name"],
                "type": output_attr["type"],
                "description": output_attr["metadata"].get("description", "")
                if output_attr["metadata"]
                else "",
            }
        )

    # Outputs from step functions
    for step in block_info["steps"]:
        if step["output_name"] and step["return_type"]:
            outputs.append(
                {
                    "name": step["output_name"],
                    "type": step["return_type"],
                    "description": "",
                }
            )

    if outputs:
        md += "| Name | Data Type | Description |\n"
        md += "|------|-----------|-------------|\n"
        for output in outputs:
            name = escape_markdown(output["name"])
            data_type = escape_markdown(output["type"])
            description = escape_markdown(output["description"])
            md += f"| {name} | `{data_type}` | {description} |\n"
    else:
        md += "No outputs available.\n"
    md += "\n"

    # State Variables
    state_attributes = [attr for attr in block_info["attributes"] if attr["state"]]
    md += "## State Variables\n\n"
    if state_attributes:
        md += "| Name | Data Type | Description |\n"
        md += "|------|-----------|-------------|\n"
        for state in state_attributes:
            name = escape_markdown(state["name"])
            data_type = escape_markdown(state["type"])
            description = escape_markdown(
                state["metadata"].get("description", "") if state["metadata"] else ""
            )
            md += f"| {name} | `{data_type}` | {description} |\n"
    else:
        md += "No state variables available.\n"
    md += "\n"

    # Step Functions
    # md += "## Step Functions\n\n"
    # for step in block_info["steps"]:
    #     md += f"### {step['name']}\n\n"
    #     md += f"- **Output Name**: {step['output_name']}\n"
    #     md += f"- **Return Type**: `{step['return_type']}`\n\n"
    #     md += "#### Inputs:\n\n"
    #     if step["inputs"]:
    #         md += "| Name | Data Type | Description |\n"
    #         md += "|------|-----------|-------------|\n"
    #         for input_param in step["inputs"]:
    #             name = input_param["name"]
    #             data_type = input_param["type"]
    #             description = (
    #                 input_param["metadata"].get("description", "")
    #                 if input_param["metadata"]
    #                 else ""
    #             )
    #             md += f"| {name} | `{data_type}` | {description} |\n"
    #         md += "\n"
    #     else:
    #         md += "No inputs for this step function.\n\n"

    return md


def generate_block_markdown_details(block_name: str):
    block_class = get_block_class(block_name)
    if not block_class:
        return f"Block {block_name} not found"
    block_info = get_block_info(block_class)
    markdown_content = generate_markdown(block_info)
    return markdown_content


# Example usage
if __name__ == "__main__":
    block_name = "Slice"
    markdown_content = generate_block_markdown_details(block_name)
    pass
    # if len(sys.argv) != 3:
    #     print("Usage: python script.py <input_path> <output_dir>")
    #     sys.exit(1)

    try:
        input_path = sys.argv[1]
    except IndexError:
        input_path = os.path.join("smartspace", "blocks")
    try:
        output_dir = sys.argv[2]
    except IndexError:
        output_dir = os.path.join("docs", "block-reference")
    generate_block_docs(input_path, output_dir)
