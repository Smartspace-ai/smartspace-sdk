import pypandoc  # type: ignore
import pytest

# Import the block under test
from smartspace.blocks.MarkdownToRTF import MarkdownToRTF


@pytest.fixture(scope="session")
def ensure_pandoc():
    try:
        pypandoc.get_pandoc_path()
    except Exception:
        try:
            pypandoc.download_pandoc()
        except Exception:
            pytest.skip("pandoc not available and download failed")
    # Verify after potential download
    try:
        pypandoc.get_pandoc_path()
    except Exception:
        pytest.skip("pandoc not available after download")


@pytest.mark.asyncio
async def test_markdown_to_rtf_success(ensure_pandoc):
    block = MarkdownToRTF()
    input_md = "# Title\n\nSome **bold** text."

    r = await block.process(input_md)

    assert isinstance(r, str)
    # RTF output should include RTF header and plain text content
    assert "{\\rtf" in r
    assert "Title" in r
    assert "bold" in r


@pytest.mark.asyncio
async def test_markdown_to_rtf_empty_input(ensure_pandoc):
    block = MarkdownToRTF()

    r = await block.process("")

    assert isinstance(r, str)
    assert "{\\rtf" in r


@pytest.mark.asyncio
async def test_markdown_to_rtf_single_run_enforced(ensure_pandoc):
    block = MarkdownToRTF()

    # First run should work
    await block.process("one")

    # Second run on same instance should raise BlockError
    from smartspace.core import BlockError

    with pytest.raises(BlockError):
        await block.process("two")


def test_markdown_to_rtf_metadata_and_step_properties():
    # Class-level metadata attached by @metadata
    meta = getattr(MarkdownToRTF, "metadata", {})
    assert meta.get("label") == "markdown-to-rtf converter"
    assert meta.get("description") == "Converts Markdown input to RTF format."
    assert isinstance(meta.get("category"), dict)
    assert meta["category"].get("name") == "Custom"

    # Step exists and has correct output name per decorator
    block = MarkdownToRTF()
    step_attr = getattr(block, "process")
    # The output pin name should be rtf_output
    assert getattr(step_attr, "_output_name", None) == "rtf_output"
