import ast
import logging
import os
from typing import Any, Dict, List, TypedDict

logging.basicConfig(level=logging.DEBUG, filename="block_doc_generator.log")
logger = logging.getLogger(__name__)


def print_ast(node, indent=""):
    """Recursively print the AST structure."""
    logger.debug(f"{indent}{type(node).__name__}")
    for field, value in ast.iter_fields(node):
        if isinstance(value, list):
            for item in value:
                if isinstance(item, ast.AST):
                    logger.debug(f"{indent}  {field}:")
                    print_ast(item, indent + "    ")
        elif isinstance(value, ast.AST):
            logger.debug(f"{indent}  {field}:")
            print_ast(value, indent + "    ")
        else:
            logger.debug(f"{indent}  {field}: {value}")


def parse_class(class_def: ast.ClassDef) -> Dict[str, Any]:
    class_info = {
        "name": class_def.name,
        "description": "",
        "config": [],
        "inputs": [],
        "outputs": [],
    }

    logger.debug(f"Parsing class: {class_def.name}")
    logger.debug("Class AST:")
    print_ast(class_def)

    # Parse metadata decorator
    for decorator in class_def.decorator_list:
        if (
            isinstance(decorator, ast.Call)
            and isinstance(decorator.func, ast.Name)
            and decorator.func.id == "metadata"
        ):
            for keyword in decorator.keywords:
                if keyword.arg == "description":
                    class_info["description"] = ast.literal_eval(keyword.value)
                    logger.debug(
                        f"Found class description: {class_info['description']}"
                    )

    # Parse class body
    for node in class_def.body:
        if isinstance(node, ast.AnnAssign):
            target = node.target.id
            annotation = node.annotation

            if isinstance(annotation, ast.Subscript):
                value_type = annotation.value
                if isinstance(value_type, ast.Name):
                    value_id = value_type.id
                    if value_id == "Config":
                        config_type = get_annotation_type(annotation.slice)
                        class_info["config"].append(
                            {
                                "name": target,
                                "type": config_type,
                            }
                        )
                        logger.debug(f"Found Config: {target} of type {config_type}")
                    elif value_id == "Output":
                        output_type = get_annotation_type(annotation.slice)
                        class_info["outputs"].append(
                            {
                                "name": target,
                                "type": get_annotation_type(annotation.slice),
                            }
                        )
                        logger.debug(f"Found output: {target} of type {output_type}")

        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            logger.debug(f"Examining function: {node.name}")
            logger.debug("Function AST:")
            print_ast(node)

            is_step = False
            output_name = None
            for decorator in node.decorator_list:
                logger.debug(f"Examining decorator: {ast.dump(decorator)}")
                if isinstance(decorator, ast.Name) and decorator.id == "step":
                    is_step = True
                elif (
                    isinstance(decorator, ast.Call)
                    and isinstance(decorator.func, ast.Name)
                    and decorator.func.id == "step"
                ):
                    is_step = True
                    for keyword in decorator.keywords:
                        if keyword.arg == "output_name":
                            output_name = ast.literal_eval(keyword.value)
                            logger.debug(f"Found output_name: {output_name}")

            if is_step:
                logger.debug(f"Found @step decorator on function: {node.name}")

                # Parse inputs (function parameters)
                for arg in node.args.args[1:]:  # Skip 'self'
                    arg_type = (
                        get_annotation_type(arg.annotation) if arg.annotation else "Any"
                    )
                    class_info["inputs"].append({"name": arg.arg, "type": arg_type})
                    logger.debug(f"Found input: {arg.arg} of type {arg_type}")

                # Parse output
                if output_name:
                    output_type = (
                        get_annotation_type(node.returns) if node.returns else "Any"
                    )
                    class_info["outputs"].append(
                        {"name": output_name, "type": output_type}
                    )
                    logger.debug(f"Added output: {output_name} of type {output_type}")
                else:
                    logger.warning(f"No output_name found for function: {node.name}")
            else:
                logger.debug(f"Function {node.name} is not decorated with @step")

    logger.debug(f"Finished parsing class {class_def.name}")
    logger.debug(f"Class info: {class_info}")
    return class_info


def get_annotation_type(annotation):
    try:
        if isinstance(annotation, ast.Name):
            return annotation.id
        elif isinstance(annotation, ast.Subscript):
            value_type = get_annotation_type(annotation.value)
            slice_type = get_annotation_type(annotation.slice)
            return f"{value_type}[{slice_type}]"
        elif isinstance(annotation, ast.Index):  # For Python < 3.9
            return get_annotation_type(annotation.value)
        elif isinstance(annotation, ast.Constant):  # For Python >= 3.9
            return annotation.value
        elif isinstance(
            annotation, ast.BinOp
        ):  # For union types like list[Any] | dict[str, Any]
            left = get_annotation_type(annotation.left)
            right = get_annotation_type(annotation.right)
            return f"{left} | {right}"
        elif isinstance(annotation, ast.Tuple):  # For tuple types
            return f"Tuple[{', '.join(get_annotation_type(elem) for elem in annotation.elts)}]"
        else:
            logger.warning(f"Unknown annotation type: {type(annotation)}")
            return "Any"
    except Exception as e:
        logger.error(f"Error in get_annotation_type: {e}")
        return "Any"


class MarkdownObject(TypedDict):
    overview: str
    config: str
    inputs: str
    outputs: str


def generate_full_markdown(class_info: Dict[str, Any]) -> str:
    md = f"# {class_info['name']}\n\n"
    md += "## Overview\n\n"
    md += f"{class_info['description']}\n\n"
    md += '!!! info "Details"\n\n'

    # Config
    md += '    === "Config"\n\n'
    if class_info["config"]:
        md += "        | Name | Data Type | Description | Default Value | Notes |\n"
        md += "        |------|-----------|-------------|---------------|-------|\n"
        for config in class_info["config"]:
            md += f"        | {config['name']} | `{config['type']}` | | | |\n"
    else:
        md += "        No configuration options available.\n"
    md += "\n"

    # Inputs
    md += '    === "Inputs"\n\n'
    if class_info["inputs"]:
        md += "        | Name | Data Type | Description | Notes |\n"
        md += "        |------|-----------|-------------|-------|\n"
        for input in class_info["inputs"]:
            md += f"        | {input['name']} | `{input['type']}` | | |\n"
    else:
        md += "        No inputs available.\n"
    md += "\n"

    # Outputs
    md += '    === "Outputs"\n\n'
    if class_info["outputs"]:
        md += "        | Name | Data Type | Description | Notes |\n"
        md += "        |------|-----------|-------------|-------|\n"
        for output in class_info["outputs"]:
            md += f"        | {output['name']} | `{output['type']}` | | |\n"
    else:
        md += "        No outputs available.\n"
    md += "\n"

    # Add placeholder sections
    md += "## Example(s)\n\n"
    md += "## Error Handling\n\n"
    md += "## FAQ\n\n"
    md += "## See Also\n"

    return md


def generate_markdown_details(class_info: Dict[str, Any]) -> str:
    # Config
    md = '    === "Config"\n\n'
    if class_info["config"]:
        md += "        | Name | Data Type | Description | Default Value | Notes |\n"
        md += "        |------|-----------|-------------|---------------|-------|\n"
        for config in class_info["config"]:
            md += f"        | {config['name']} | `{config['type']}` | | | |\n"
    else:
        md += "        No configuration options available.\n"
    md += "\n"

    # Inputs
    md += '    === "Inputs"\n\n'
    if class_info["inputs"]:
        md += "        | Name | Data Type | Description | Notes |\n"
        md += "        |------|-----------|-------------|-------|\n"
        for input in class_info["inputs"]:
            md += f"        | {input['name']} | `{input['type']}` | | |\n"
    else:
        md += "        No inputs available.\n"
    md += "\n"

    # Outputs
    md += '    === "Outputs"\n\n'
    if class_info["outputs"]:
        md += "        | Name | Data Type | Description | Notes |\n"
        md += "        |------|-----------|-------------|-------|\n"
        for output in class_info["outputs"]:
            md += f"        | {output['name']} | `{output['type']}` | | |\n"
    else:
        md += "        No outputs available.\n"
    md += "\n"

    return md


def generate_markdown_object(class_info: Dict[str, Any]) -> MarkdownObject:
    markdown_object = MarkdownObject(
        overview=f"{class_info['description']}",
        config="",
        inputs="",
        outputs="",
    )

    # Config
    config_md = ""
    if class_info["config"]:
        config_md = "| Name | Data Type | Description | Default Value | Notes |\n"

        config_md += "|------|-----------|-------------|---------------|-------|\n"
        for config in class_info["config"]:
            config_md += "| {config['name']} | `{config['type']}` | | | |\n"
    else:
        config_md += "No configuration options available.\n"
    config_md += "\n"
    markdown_object["config"] = config_md

    # Inputs
    input_md = ""
    if class_info["inputs"]:
        input_md += "| Name | Data Type | Description | Notes |\n"
        input_md += "|------|-----------|-------------|-------|\n"
        for input in class_info["inputs"]:
            input_md += f"| {input['name']} | `{input['type']}` | | |\n"
    else:
        input_md += "No inputs available.\n"
    input_md += "\n"
    markdown_object["inputs"] = input_md

    # Outputs

    output_md = ""
    if class_info["outputs"]:
        output_md += "| Name | Data Type | Description | Notes |\n"
        output_md += "|------|-----------|-------------|-------|\n"
        for output in class_info["outputs"]:
            output_md += f"| {output['name']} | `{output['type']}` | | |\n"
    else:
        output_md += "No outputs available.\n"
    output_md += "\n"
    markdown_object["outputs"] = output_md

    return markdown_object


def process_file(file_path: str) -> List[Dict[str, Any]]:
    with open(file_path, "r") as file:
        content = file.read()

    tree = ast.parse(content)
    block_classes = []

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            # Check if the class inherits from Block
            if any(
                base.id == "Block" for base in node.bases if isinstance(base, ast.Name)
            ):
                block_classes.append(parse_class(node))

    return block_classes


def get_block_class(block_name: str):
    files = [
        os.path.join("smartspace/blocks", f)
        for f in os.listdir("smartspace/blocks")
        if f.endswith(".py")
    ]
    for file_path in files:
        block_classes = process_file(file_path)
        for class_info in block_classes:
            if class_info["name"] == block_name:
                return class_info


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
        block_classes = process_file(file_path)
        for class_info in block_classes:
            markdown_content = get_block_markdown_template()
            output_file = os.path.join(output_dir, f"{class_info['name']}.md")
            with open(output_file, "w") as f:
                f.write(markdown_content)
            print(f"Generated documentation for {class_info['name']} in {output_file}")


def generate_block_markdown_details(block_name: str):
    block_class = get_block_class(block_name)
    if not block_class:
        return f"Block {block_name} not found"
    markdown_content = generate_markdown_details(block_class)
    return markdown_content


def generate_block_markdown_overview(block_name: str):
    block_class = get_block_class(block_name)
    if not block_class:
        return f"Block {block_name} not found"
    return block_class["description"]


# Example usage
if __name__ == "__main__":
    import sys

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
