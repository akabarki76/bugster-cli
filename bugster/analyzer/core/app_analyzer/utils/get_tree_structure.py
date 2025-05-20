import os
from typing import Dict, List, Literal, TypedDict, Union

# Instead of globby, we'll use Python's glob
# Instead of zod, we'll use Python's type annotations

"""
Get the paths of the files in the source directory
"""


def get_paths(source_dir):
    # Implement a function similar to globby with gitignore support
    # This is a simplified version without gitignore support
    all_files = []

    # Walk through directory
    for root, _, files in os.walk(source_dir):
        for file in files:
            # Get the full path
            full_path = os.path.join(root, file)
            # Convert to relative path
            rel_path = os.path.relpath(full_path, source_dir)

            # Apply ignore patterns
            ignore_patterns = [
                "**/*.test.ts",
                "**/*.test.tsx",
                "**/*.test.js",
                "**/*.test.jsx",
                "**/*.spec.ts",
                "**/*.spec.tsx",
                "**/*.spec.js",
                "**/*.spec.jsx",
                "packages/**",
                "test/**",
                "tests/**",
            ]

            # Simple pattern matching (not as sophisticated as globby)
            should_ignore = False
            for pattern in ignore_patterns:
                # Convert glob pattern to simple checks
                if pattern.startswith("**/*"):
                    ext = pattern[4:]
                    if rel_path.endswith(ext):
                        should_ignore = True
                        break
                elif pattern.endswith("/**"):
                    dir_prefix = pattern[:-3]
                    if rel_path.startswith(dir_prefix):
                        should_ignore = True
                        break

            if not should_ignore:
                all_files.append(rel_path)

    all_files.sort()
    return all_files


# Define types that would be validated by zod in TypeScript
class FileNode(TypedDict):
    path: str
    name: str
    type: Literal["file"]
    extension: str


class DirectoryNode(TypedDict):
    path: str
    name: str
    type: Literal["directory"]
    children: List[Union["DirectoryNode", FileNode]]


TreeNode = Union[DirectoryNode, FileNode]

"""
Get the tree structure of the source directory
"""


def get_tree_structure(source_dir) -> TreeNode:
    # logger = get_logger()
    print("Building application structure tree...")
    paths = get_paths(source_dir)

    root_node: DirectoryNode = {
        "path": "",
        "name": os.path.basename(source_dir),
        "type": "directory",
        "children": [],
    }

    dir_map: Dict[str, DirectoryNode] = {}
    dir_map[""] = root_node

    """
    Helper function to ensure a directory path exists in the tree
    and returns the node for that directory
    """

    def ensure_directory_path(dir_path: str) -> DirectoryNode:
        # If we already have this directory in our map, return it
        if dir_path in dir_map:
            return dir_map[dir_path]

        parent_path = os.path.dirname(dir_path)
        parent_node = (
            root_node if parent_path == "." else ensure_directory_path(parent_path)
        )
        dir_name = os.path.basename(dir_path)

        dir_node: DirectoryNode = {
            "path": dir_path,
            "name": dir_name,
            "type": "directory",
            "children": [],
        }

        parent_node["children"].append(dir_node)
        dir_map[dir_path] = dir_node

        return dir_node

    for file_path in paths:
        if not file_path:
            continue

        is_directory = not os.path.splitext(file_path)[1]

        if is_directory:
            ensure_directory_path(file_path)
        else:
            dir_path = os.path.dirname(file_path)
            parent_node = (
                root_node if dir_path == "." else ensure_directory_path(dir_path)
            )
            file_name = os.path.basename(file_path)

            file_node: FileNode = {
                "path": file_path,
                "name": file_name,
                "type": "file",
                "extension": os.path.splitext(file_path)[1],
            }

            parent_node["children"].append(file_node)

    return root_node
