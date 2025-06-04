from pathlib import Path


def extract_page_folder(file_path: str) -> str:
    """Extract the first parent folder path for a given file path."""
    # Convert to Path object for easier manipulation
    path = Path(file_path)

    # Get all parts of the path
    parts = list(path.parts)

    # Remove the filename (last part)
    if parts:
        parts = parts[:-1]

    # Remove the root folder (first part like 'src' or 'app')
    if parts:
        parts = parts[1:]

    # Keep only the first remaining folder
    if parts:
        folder_path = parts[0]
    else:
        folder_path = ""

    return folder_path
