#!/usr/bin/env python3

import os
import subprocess
import zipfile
import xml.etree.ElementTree as ET
import argparse

def get_git_files(repo_path, include_untracked=False):
    """Get tracked and/or untracked files using `git ls-files`."""
    cmd = ['git', 'ls-files']
    if include_untracked:
        cmd.append('--others')
        cmd.append('--exclude-standard')

    result = subprocess.run(cmd, cwd=repo_path, stdout=subprocess.PIPE, text=True, check=True)
    return result.stdout.splitlines()

def create_zip(files, output_path):
    """Create a ZIP archive containing the specified files."""
    with zipfile.ZipFile(output_path, 'w') as zipf:
        for file in files:
            if os.path.isfile(file):
                zipf.write(file)

def create_xml(files, output_path):
    """Create an XML file listing the specified files and their contents."""
    root = ET.Element('files')
    for file in files:
        file_element = ET.SubElement(root, 'file', path=file)
        if os.path.isfile(file):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception as e:
                content = f"Error reading file: {e}"
            # Add the file's content in a child element.
            content_element = ET.SubElement(file_element, 'content')
            content_element.text = content
    tree = ET.ElementTree(root)
    tree.write(output_path, encoding='utf-8', xml_declaration=True)

def get_repo_name(repo_path):
    """Get the Git repository's name based on its path."""
    result = subprocess.run(['git', 'rev-parse', '--show-toplevel'], cwd=repo_path, stdout=subprocess.PIPE, text=True, check=True)
    repo_path = result.stdout.strip()
    return os.path.basename(repo_path)

def print_file_tree(files):
    """Print out the file tree of files that would be exported."""
    for file in files:
        print(file)

def main():
    parser = argparse.ArgumentParser(description="Export Git repository files to a specified format.")
    parser.add_argument('path', default='.', nargs='?', help="Path to the Git repository (default is current directory).")
    parser.add_argument('-f', '--format', choices=['zip', 'xml'], help="Output format: zip or xml.")
    parser.add_argument('--untracked', action='store_true', help="Include untracked files.")
    parser.add_argument('--info', action='store_true', help="List out the files that would be exported.")
    args = parser.parse_args()

    if not args.format and not args.info:
        parser.print_usage()
        return

    # Use the specified or default path
    repo_path = args.path

    if args.info:
        # Gather all relevant files
        files = get_git_files(repo_path, include_untracked=args.untracked)
        # Print file tree
        print_file_tree(files)
        return

    if not args.format:
        print("Error: --format is required when not using --info.")
        return

    # Get the repository name and output filename
    repo_name = get_repo_name(repo_path)
    output_filename = f"{repo_name}.{args.format}"

    # Gather all relevant files
    files = get_git_files(repo_path, include_untracked=args.untracked)

    # Handle output format
    if args.format == 'zip':
        create_zip(files, output_filename)
    elif args.format == 'xml':
        create_xml(files, output_filename)

    print(f"Files successfully exported to {output_filename}.")

if __name__ == "__main__":
    main()
