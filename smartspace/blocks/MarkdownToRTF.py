import pypandoc

from smartspace.core import Block, metadata, step


@metadata(
    category={"name": "Custom", "description": "Custom blocks added by SmartSpace"},
    description="Converts Markdown input to RTF format.",
    label="markdown-to-rtf converter",
)
class MarkdownToRTF(Block):
    @step(output_name="rtf_output")
    async def process(self, input: str) -> str:
        return pypandoc.convert_text(
            input, "rtf", format="md", extra_args=["--standalone"]
        )
