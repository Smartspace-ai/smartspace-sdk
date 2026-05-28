import pypandoc

from smartspace.core import Block, metadata, step
from smartspace.enums import BlockCategory


@metadata(
    category=BlockCategory.TRANSFORM,
    description="Converts Markdown input to RTF format.",
    label="markdown to rtf, format conversion, document conversion, pandoc",
)
class MarkdownToRTF(Block):
    @step(output_name="rtf_output")
    async def process(self, input: str) -> str:
        return pypandoc.convert_text(
            input, "rtf", format="md", extra_args=["--standalone"]
        )
