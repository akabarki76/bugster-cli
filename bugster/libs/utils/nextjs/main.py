from pathlib import Path
from typing import List


def find_page_files(project_root: str) -> List[str]:
    """Find all Next.js page files for both Pages Router and App Router."""
    project_path = Path(project_root)
    page_files = []

    # Pages Router - find all files except special ones and API routes
    for pages_dir in ["pages", "src/pages"]:
        pages_path = project_path / pages_dir
        if pages_path.exists():
            for ext in ["*.js", "*.jsx", "*.ts", "*.tsx"]:
                for file in pages_path.rglob(ext):
                    if is_page_file(file, "pages"):
                        page_files.append(str(file))

    # App Router - find page.* files only
    for app_dir in ["app", "src/app"]:
        app_path = project_path / app_dir
        if app_path.exists():
            for ext in ["js", "jsx", "ts", "tsx"]:
                for file in app_path.rglob(f"page.{ext}"):
                    # Skip private folders (starting with _)
                    if not any(part.startswith("_") for part in file.parts):
                        page_files.append(str(file))

    return page_files


def is_page_file(file_path: Path, router_type: str) -> bool:
    """Check if a file is actually a page (not API route or special file)."""
    filename = file_path.stem

    # Skip special Next.js files
    special_files = ["_document", "_app", "_error", "404", "500", "_middleware"]
    if filename in special_files:
        return False

    # Skip API routes in Pages Router
    if router_type == "pages" and "api" in file_path.parts:
        return False

    return True
