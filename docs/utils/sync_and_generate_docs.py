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
from typing import Dict, List

import yaml
from block_doc_generator import generate_block_docs_temp

# Add project root to path to import block_doc_generator
project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.insert(0, project_root)


def clone_or_update_repo(repo_url: str, target_dir: str, force_clean: bool = False) -> None:
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
                    subprocess.run(["git", "-C", target_dir, "reset", "--hard"], check=True)
                    subprocess.run(["git", "-C", target_dir, "clean", "-fd"], check=True)
                    subprocess.run(["git", "-C", target_dir, "pull"], check=True)
                except subprocess.CalledProcessError:
                    print("Reset and pull failed. Removing directory and cloning fresh...")
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

    copied_files = []
    source_blocks_dir = os.path.join(source_dir, "app", "blocks")

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

    # Get existing blocks to avoid duplicates (case-insensitive)
    existing_blocks = set()
    existing_blocks_lowercase = set()
    for section in smartspace_section:
        if isinstance(section, dict):
            for category, blocks in section.items():
                if isinstance(blocks, list):
                    for block in blocks:
                        if isinstance(block, dict):
                            for _, path in block.items():
                                if isinstance(path, str) and path.startswith(
                                    "block-reference/"
                                ):
                                    block_name = path.split("/")[-1].replace(".md", "")
                                    existing_blocks.add(block_name)
                                    existing_blocks_lowercase.add(block_name.lower())

    # Update navigation with new blocks
    updated = False
    for category, blocks in new_blocks.items():
        # Find or create category section
        category_section = None
        for section in smartspace_section:
            if isinstance(section, dict) and category in section:
                category_section = section[category]
                break

        if category_section is None:
            # Create new category section
            category_section = []
            smartspace_section.append({category: category_section})
            updated = True

        # Add new blocks to category
        for block in sorted(blocks):
            if block not in existing_blocks and block.lower() not in existing_blocks_lowercase:
                category_section.append({block: f"block-reference/{block}.md"})
                print(f"Added {block} to {category} section")
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
