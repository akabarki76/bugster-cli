import os


def get_all_files(directory):
    """Get all files in a directory."""
    file_paths = []

    for root, dirs, files in os.walk(directory):
        if "example" in root:
            continue

        for file in files:
            file_paths.append(os.path.join(root, file))

    return file_paths
