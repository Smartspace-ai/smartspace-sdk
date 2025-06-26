#!/usr/bin/env python3
"""
Script to sync blocks from external repository and generate documentation.
This script:
1. Clones/updates the Smartspace-ai-api repository
2. Copies block files to the local smartspace_blocks directory
3. Generates documentation for all blocks
4. Updates mkdocs.yml navigation if new blocks are found
"""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import yaml
from block_doc_generator import generate_block_docs_temp

# Add project root to path to import block_doc_generator
project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.insert(0, project_root)


def clone_or_update_repo(
    repo_url: str, target_dir: str, force_clean: bool = False
) -> None:
    """Clone repository if it doesn't exist, otherwise pull latest changes."""
    if os.path.exists(target_dir):
        if force_clean:
            print(f"Force clean enabled. Removing existing directory: {target_dir}")
            shutil.rmtree(target_dir)
            print(f"Cloning repository to {target_dir}")
            subprocess.run(["git", "clone", repo_url, target_dir], check=True)
        else:
            print(f"Updating repository in {target_dir}")
            try:
                subprocess.run(["git", "-C", target_dir, "pull"], check=True)
            except subprocess.CalledProcessError as e:
                print(f"Git pull failed: {e}")
                print("Attempting to reset and pull again...")
                try:
                    # Reset any local changes
                    subprocess.run(
                        ["git", "-C", target_dir, "reset", "--hard"], check=True
                    )
                    subprocess.run(
                        ["git", "-C", target_dir, "clean", "-fd"], check=True
                    )
                    subprocess.run(["git", "-C", target_dir, "pull"], check=True)
                except subprocess.CalledProcessError:
                    print(
                        "Reset and pull failed. Removing directory and cloning fresh..."
                    )
                    shutil.rmtree(target_dir)
                    subprocess.run(["git", "clone", repo_url, target_dir], check=True)
    else:
        print(f"Cloning repository to {target_dir}")
        subprocess.run(["git", "clone", repo_url, target_dir], check=True)


def copy_block_files(source_dir: str, target_dir: str) -> List[str]:
    """Copy block Python files from source to target directory."""
    # Create target directory if it doesn't exist
    os.makedirs(target_dir, exist_ok=True)

    # Clear existing files in target directory
    for file in os.listdir(target_dir):
        if file.endswith(".py"):
            os.remove(os.path.join(target_dir, file))

    copied_files: List[str] = []
    source_blocks_dir = os.path.join(source_dir, "app", "blocks", "native")

    if not os.path.exists(source_blocks_dir):
        print(f"Warning: Source blocks directory not found: {source_blocks_dir}")
        return copied_files

    # Copy all Python files from blocks directory
    for root, dirs, files in os.walk(source_blocks_dir):
        for file in files:
            if file.endswith(".py") and not file.startswith("__"):
                source_file = os.path.join(root, file)
                target_file = os.path.join(target_dir, file)
                shutil.copy2(source_file, target_file)
                copied_files.append(target_file)
                print(f"Copied {file}")

    return copied_files


def update_mkdocs_nav(mkdocs_path: str, new_blocks: Dict[str, List[str]]) -> bool:
    """Update mkdocs.yml navigation with new blocks."""
    with open(mkdocs_path, "r") as f:
        mkdocs_config = yaml.safe_load(f)

    # Find the Block Reference section in navigation
    nav = mkdocs_config.get("nav", [])
    block_ref_section = None

    for item in nav:
        if isinstance(item, dict) and "Block Reference" in item:
            block_ref_section = item["Block Reference"]
            break

    if not block_ref_section:
        print("Warning: Could not find 'Block Reference' section in mkdocs.yml")
        return False

    # Find SmartSpace Blocks subsection
    smartspace_section = None
    for item in block_ref_section:
        if isinstance(item, dict) and "SmartSpace Blocks" in item:
            smartspace_section = item["SmartSpace Blocks"]
            break

    if not smartspace_section:
        print("Warning: Could not find 'SmartSpace Blocks' section in mkdocs.yml")
        return False

    # Track existing blocks with their locations
    existing_blocks_by_location: Dict[
        str, Union[Dict[str, Tuple[str, int, int]], Dict[str, int]]
    ] = {
        "SmartSpace": {},  # {block_name: (category, section_index, block_index)}
        "Obsolete": {},  # {block_name: block_index}
    }
    existing_blocks_lowercase = {}  # {lowercase_name: actual_name}
    all_existing_blocks = {}  # {actual_name: (location_type, category)}

    # First, check all non-SmartSpace sections in Block Reference
    for item in block_ref_section:
        if isinstance(item, dict):
            for section_name, section_content in item.items():
                # Skip SmartSpace Blocks and Obsolete (handled separately)
                if section_name in ["SmartSpace Blocks", "Obsolete"]:
                    continue

                # Check direct block entries
                if isinstance(section_content, list):
                    for block_item in section_content:
                        if isinstance(block_item, dict):
                            for block_title, path in block_item.items():
                                if isinstance(path, str) and path.startswith(
                                    "block-reference/"
                                ):
                                    block_name = path.split("/")[-1].replace(".md", "")
                                    existing_blocks_lowercase[block_name.lower()] = (
                                        block_name
                                    )
                                    all_existing_blocks[block_name] = (
                                        "Other",
                                        section_name,
                                    )

                # Check nested categories (like in Misc section)
                elif isinstance(section_content, dict):
                    for subsection_name, subsection_blocks in section_content.items():
                        if isinstance(subsection_blocks, list):
                            for block_item in subsection_blocks:
                                if isinstance(block_item, dict):
                                    for block_title, path in block_item.items():
                                        if isinstance(path, str) and path.startswith(
                                            "block-reference/"
                                        ):
                                            block_name = path.split("/")[-1].replace(
                                                ".md", ""
                                            )
                                            existing_blocks_lowercase[
                                                block_name.lower()
                                            ] = block_name
                                            all_existing_blocks[block_name] = (
                                                "Other",
                                                f"{section_name}/{subsection_name}",
                                            )

    # Check SmartSpace Blocks section
    for section_idx, section in enumerate(smartspace_section):
        if isinstance(section, dict):
            for category, blocks in section.items():
                if isinstance(blocks, list):
                    for block_idx, block in enumerate(blocks):
                        if isinstance(block, dict):
                            for block_title, path in block.items():
                                if isinstance(path, str) and path.startswith(
                                    "block-reference/"
                                ):
                                    block_name = path.split("/")[-1].replace(".md", "")
                                    existing_blocks_by_location["SmartSpace"][
                                        block_name
                                    ] = (category, section_idx, block_idx)
                                    existing_blocks_lowercase[block_name.lower()] = (
                                        block_name
                                    )
                                    all_existing_blocks[block_name] = (
                                        "SmartSpace",
                                        category,
                                    )

    # Also check Obsolete section
    obsolete_section_idx = None
    for idx, item in enumerate(block_ref_section):
        if isinstance(item, dict) and "Obsolete" in item:
            obsolete_section_idx = idx
            obsolete_blocks = item["Obsolete"]
            if isinstance(obsolete_blocks, list):
                for block_idx, block in enumerate(obsolete_blocks):
                    if isinstance(block, dict):
                        for block_title, path in block.items():
                            if isinstance(path, str) and path.startswith(
                                "block-reference/"
                            ):
                                block_name = path.split("/")[-1].replace(".md", "")
                                existing_blocks_by_location["Obsolete"][block_name] = (
                                    block_idx
                                )
                                existing_blocks_lowercase[block_name.lower()] = (
                                    block_name
                                )
                                all_existing_blocks[block_name] = ("Obsolete", None)

    # Find or create Obsolete section
    obsolete_section = None
    for i, item in enumerate(block_ref_section):
        if isinstance(item, dict) and "Obsolete" in item:
            obsolete_section = item["Obsolete"]
            break

    if obsolete_section is None and "Obsolete" in new_blocks and new_blocks["Obsolete"]:
        # Create Obsolete section if it doesn't exist and we have obsolete blocks
        obsolete_section = []
        # Find where to insert Obsolete section (after SmartSpace Blocks)
        smartspace_index = None
        for i, item in enumerate(block_ref_section):
            if isinstance(item, dict) and "SmartSpace Blocks" in item:
                smartspace_index = i
                break
        if smartspace_index is not None:
            block_ref_section.insert(
                smartspace_index + 1, {"Obsolete": obsolete_section}
            )
        else:
            block_ref_section.append({"Obsolete": obsolete_section})

    # Track which blocks to keep (handle case variations)
    blocks_to_keep = {}  # {lowercase_name: (actual_name, preferred_category)}
    blocks_to_remove: List[Tuple[str, Optional[str], Optional[int], int, str]] = []

    # First pass: identify all blocks and their preferred locations
    for category, blocks in new_blocks.items():
        for block in blocks:
            block_lower = block.lower()

            # Check if this block already exists in other sections (non-SmartSpace)
            if block_lower in existing_blocks_lowercase:
                existing_name = existing_blocks_lowercase[block_lower]
                if existing_name in all_existing_blocks:
                    location_type, existing_category = all_existing_blocks[
                        existing_name
                    ]
                    if location_type == "Other":
                        # Block exists in non-SmartSpace section, skip it
                        print(
                            f"Skipping {block} - already exists in {existing_category} section"
                        )
                        continue

            if block_lower not in blocks_to_keep:
                blocks_to_keep[block_lower] = (block, category)
            else:
                # If we already have this block (case-insensitive), prefer non-obsolete category
                existing_name, existing_cat = blocks_to_keep[block_lower]
                if existing_cat == "Obsolete" and category != "Obsolete":
                    blocks_to_keep[block_lower] = (block, category)

    # Remove all existing entries that are duplicates (case-insensitive) or in wrong location
    for block_lower, (preferred_name, preferred_category) in blocks_to_keep.items():
        # Find all case variations of this block in existing structure
        for existing_name, (location_type, existing_category) in list(
            all_existing_blocks.items()
        ):
            if existing_name.lower() == block_lower:
                # Determine if we need to remove this entry
                should_remove = False

                # Remove if it's a case variation of the preferred name
                if existing_name != preferred_name:
                    should_remove = True
                    print(
                        f"Removing case variation: {existing_name} (keeping {preferred_name})"
                    )

                # Remove if it's in the wrong category
                elif existing_category != preferred_category:
                    should_remove = True
                    print(
                        f"Moving {existing_name} from {existing_category} to {preferred_category}"
                    )

                if should_remove:
                    if (
                        location_type == "SmartSpace"
                        and existing_name in existing_blocks_by_location["SmartSpace"]
                    ):
                        cat, sec_idx, blk_idx = existing_blocks_by_location[
                            "SmartSpace"
                        ][existing_name]
                        blocks_to_remove.append(
                            ("SmartSpace", cat, sec_idx, blk_idx, existing_name)
                        )
                    elif (
                        location_type == "Obsolete"
                        and existing_name in existing_blocks_by_location["Obsolete"]
                    ):
                        blk_idx = existing_blocks_by_location["Obsolete"][existing_name]
                        blocks_to_remove.append(
                            ("Obsolete", None, None, blk_idx, existing_name)
                        )

    # Variable to track if updates were made
    updated = False

    # Remove blocks from incorrect locations (in reverse order to maintain indices)
    for location_type, cat, sec_idx, blk_idx, block_name in sorted(
        blocks_to_remove, key=lambda x: (x[0], x[2] or 0, x[3]), reverse=True
    ):
        if location_type == "SmartSpace":
            # Remove from SmartSpace section
            section = smartspace_section[sec_idx]
            if isinstance(section, dict) and cat in section:
                blocks_list = section[cat]
                if 0 <= blk_idx < len(blocks_list):
                    del blocks_list[blk_idx]
                    print(
                        f"Removed {block_name} from {cat} section (will move to correct location)"
                    )
                    updated = True
        elif location_type == "Obsolete" and obsolete_section is not None:
            # Remove from Obsolete section
            if 0 <= blk_idx < len(obsolete_section):
                del obsolete_section[blk_idx]
                print(
                    f"Removed {block_name} from Obsolete section (will move to correct location)"
                )
                updated = True

    # Update navigation with new blocks using deduplicated list
    for block_lower, (block_name, preferred_category) in blocks_to_keep.items():
        # Check if this block already exists with the correct name and category
        if block_name in all_existing_blocks:
            location_type, existing_category = all_existing_blocks[block_name]
            if existing_category == preferred_category:
                # Block already exists in correct location, skip
                continue

        if preferred_category == "Obsolete":
            # Handle Obsolete blocks
            if obsolete_section is not None:
                # Only add if not already present
                block_exists = any(
                    isinstance(item, dict) and block_name in item
                    for item in obsolete_section
                )
                if not block_exists:
                    obsolete_section.append(
                        {block_name: f"block-reference/{block_name}.md"}
                    )
                    print(f"Added {block_name} to Obsolete section")
                    updated = True
        else:
            # Handle regular categories under SmartSpace Blocks
            category_section = None
            for section in smartspace_section:
                if isinstance(section, dict) and preferred_category in section:
                    category_section = section[preferred_category]
                    break

            if category_section is None:
                # Create new category section
                category_section = []
                smartspace_section.append({preferred_category: category_section})
                updated = True

            # Check if block already exists in this category
            block_exists = any(
                isinstance(item, dict) and block_name in item
                for item in category_section
            )

            if not block_exists:
                category_section.append(
                    {block_name: f"block-reference/{block_name}.md"}
                )
                print(f"Added {block_name} to {preferred_category} section")
                updated = True

    if updated:
        # Sort categories and blocks within each category
        for section in smartspace_section:
            if isinstance(section, dict):
                for category, blocks in section.items():
                    if isinstance(blocks, list):
                        # Sort blocks by name
                        blocks.sort(
                            key=lambda x: list(x.keys())[0]
                            if isinstance(x, dict)
                            else x
                        )

        # Write updated mkdocs.yml
        with open(mkdocs_path, "w") as f:
            yaml.dump(mkdocs_config, f, default_flow_style=False, sort_keys=False)

        print("Updated mkdocs.yml with new blocks")

    return updated


def main():
    parser = argparse.ArgumentParser(
        description="Sync blocks and generate documentation"
    )
    parser.add_argument(
        "--repo-url",
        default="https://github.com/Smartspace-ai/Smartspace-ai-api",
        help="External repository URL",
    )
    parser.add_argument("--temp-dir", help="Temporary directory for cloning repo")
    parser.add_argument(
        "--skip-sync",
        action="store_true",
        help="Skip repository sync, use existing files",
    )
    parser.add_argument(
        "--force-clean",
        action="store_true",
        help="Force clean clone instead of pull (removes existing repo)",
    )
    args = parser.parse_args()

    # Determine project root (sync_and_generate_docs.py is in docs/utils/)
    project_root = Path(__file__).parent.parent.parent

    # Set up directories
    temp_dir = args.temp_dir or tempfile.mkdtemp(prefix="smartspace_sync_")
    blocks_dir = project_root / "docs" / "utils" / "smartspace_blocks"
    docs_dir = project_root / "docs" / "block-reference"
    mkdocs_path = project_root / "mkdocs.yml"

    try:
        if not args.skip_sync:
            # Clone or update external repository
            print(f"Syncing repository from {args.repo_url}")
            clone_or_update_repo(args.repo_url, temp_dir, args.force_clean)

            # Copy block files
            print(f"\nCopying block files to {blocks_dir}")
            copied_files = copy_block_files(temp_dir, str(blocks_dir))
            print(f"Copied {len(copied_files)} block files")

        # Generate documentation
        print(f"\nGenerating documentation in {docs_dir}")
        new_blocks = generate_block_docs_temp(str(blocks_dir), str(docs_dir))

        # Update mkdocs.yml
        if new_blocks:
            print("\nUpdating mkdocs.yml navigation")
            update_mkdocs_nav(str(mkdocs_path), new_blocks)

        print("\nDocumentation generation completed successfully!")

    finally:
        # Clean up temporary directory if it was created by us
        if not args.temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


if __name__ == "__main__":
    main()
