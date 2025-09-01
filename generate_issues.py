#!/usr/bin/env python3
"""
Script to generate individual .txt files from the prompt.jsonl file
Each file represents an issue with the content of the prompt.
"""

import json
import os
import re

def sanitize_filename(filename):
    """
    Sanitizes the filename by removing invalid characters
    and replacing them with underscores.
    """
    # Replace special characters with underscores
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Replace periods with underscores except the final one for extension
    filename = filename.replace('.', '_')
    # Limit the length of the filename
    if len(filename) > 200:
        filename = filename[:200]
    return filename

def generate_issue_files(input_file, output_dir):
    """
    Generates individual .txt files from the JSONL file.
    
    Args:
        input_file (str): Path to the prompt.jsonl file
        output_dir (str): Directory where .txt files will be saved
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Counters for statistics
    total_processed = 0
    total_created = 0
    issue_id = 1
    
    print(f"Processing file: {input_file}")
    print(f"Output directory: {output_dir}")
    print("-" * 50)
    
    with open(input_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            try:
                # Parse each JSON line
                data = json.loads(line.strip())
                
                namespace = data.get('namespace', '')
                prompt = data.get('prompt', '')
                
                if not namespace or not prompt:
                    print(f"Line {line_num}: Incomplete data (empty namespace or prompt)")
                    continue
                
                # Use simple name for the file
                filename = f'issue-{issue_id}.txt'
                filepath = os.path.join(output_dir, filename)
                
                # Create issue content including namespace and code location
                issue_content = f"**Namespace:** `{namespace}`\n\n**Source Code Location:** The project source code is located in the `Source_Code/` directory.\n\n{prompt}\n"
                
                # Write the file
                with open(filepath, 'w', encoding='utf-8') as issue_file:
                    issue_file.write(issue_content)
                
                total_created += 1
                issue_id += 1
                print(f"✓ Created: {filename} (namespace: {namespace})")
                
            except json.JSONDecodeError as e:
                print(f"Error in line {line_num}: Invalid JSON - {e}")
            except Exception as e:
                print(f"Error in line {line_num}: {e}")
            
            total_processed += 1
    
    print("-" * 50)
    print(f"Processing completed:")
    print(f"  - Total lines processed: {total_processed}")
    print(f"  - Files successfully created: {total_created}")
    print(f"  - Errors: {total_processed - total_created}")

def main():
    # File paths
    input_file = "path/prompt.jsonl"
    output_dir = "path/individual_issues"
    
    # Verify that the input file exists
    if not os.path.exists(input_file):
        print(f"Error: File {input_file} does not exist.")
        return
    
    # Generate issue files
    generate_issue_files(input_file, output_dir)

if __name__ == "__main__":
    main()
