import pytest

from smartspace.blocks import load


@pytest.mark.asyncio
async def test_deprecated_blocks_have_replacements():
    blocks = await load()

    for block_name, versions in blocks.all.items():
        for version_name, block_interface in versions.items():
            if block_interface.metadata.deprecated:
                replacement = blocks.find(
                    block_interface.metadata.deprecated.replacement, "*"
                )
                assert replacement is not None, (
                    f"Replacement for {block_name} ({version_name}) is {block_interface.metadata.deprecated.replacement} but it could not be found"
                )
