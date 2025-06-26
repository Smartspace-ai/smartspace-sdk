#!/usr/bin/env python3
"""
Script to clean up duplicates in mkdocs.yml
"""

import yaml
import sys
from pathlib import Path

def clean_mkdocs_duplicates(mkdocs_path: str):
    """Clean up duplicate blocks in mkdocs.yml"""
    
    with open(mkdocs_path, 'r') as f:
        mkdocs_config = yaml.safe_load(f)
    
    nav = mkdocs_config.get('nav', [])
    seen_blocks_lower = {}  # {lowercase_name: (actual_name, location)}
    duplicates_removed = []
    
    def process_block_list(blocks_list, section_path):
        """Process a list of blocks and remove duplicates"""
        cleaned_list = []
        
        for item in blocks_list:
            if isinstance(item, dict):
                for block_name, path in item.items():
                    if isinstance(path, str) and path.startswith('block-reference/'):
                        block_lower = block_name.lower()
                        
                        # Check if we've seen this block before (case-insensitive)
                        if block_lower in seen_blocks_lower:
                            existing_name, existing_location = seen_blocks_lower[block_lower]
                            duplicates_removed.append(f"{block_name} in {section_path} (keeping {existing_name} in {existing_location})")
                        else:
                            # First time seeing this block
                            seen_blocks_lower[block_lower] = (block_name, section_path)
                            cleaned_list.append(item)
                    else:
                        cleaned_list.append(item)
            else:
                cleaned_list.append(item)
        
        return cleaned_list
    
    # Process the navigation
    for nav_item in nav:
        if isinstance(nav_item, dict) and 'Block Reference' in nav_item:
            block_ref = nav_item['Block Reference']
            
            # Process each section in Block Reference
            for i, section in enumerate(block_ref):
                if isinstance(section, dict):
                    for section_name, section_content in section.items():
                        if section_name == 'SmartSpace Blocks':
                            # Process SmartSpace Blocks categories
                            for j, subsection in enumerate(section_content):
                                if isinstance(subsection, dict):
                                    for category_name, category_blocks in subsection.items():
                                        if isinstance(category_blocks, list):
                                            cleaned = process_block_list(category_blocks, f"SmartSpace Blocks/{category_name}")
                                            subsection[category_name] = cleaned
                        
                        elif isinstance(section_content, list):
                            # Direct block list (like Obsolete)
                            cleaned = process_block_list(section_content, section_name)
                            section[section_name] = cleaned
    
    # Write back the cleaned configuration
    with open(mkdocs_path, 'w') as f:
        yaml.dump(mkdocs_config, f, default_flow_style=False, sort_keys=False)
    
    print(f"Cleaned mkdocs.yml - removed {len(duplicates_removed)} duplicates:")
    for dup in duplicates_removed:
        print(f"  - {dup}")

if __name__ == "__main__":
    project_root = Path(__file__).parent.parent.parent
    mkdocs_path = project_root / "mkdocs.yml"
    clean_mkdocs_duplicates(str(mkdocs_path))