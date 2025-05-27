import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Set


class ImportTreeGenerator:
    """
    This class analyzes a Next.js application and generates a tree structure
    showing all file imports and their dependencies recursively.
    """

    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path).resolve()
        self.processed_files: Set[str] = set()
        self.import_tree: Dict[str, Dict] = {}
        self.file_extensions = {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"}

        # Common Next.js directories to scan
        self.scan_dirs = [
            "src",
            "pages",
            "app",
            "components",
            "lib",
            "utils",
            "hooks",
            "styles",
        ]

    def is_valid_file(self, filepath: Path) -> bool:
        """Check if file should be analyzed for imports."""
        return (
            filepath.suffix in self.file_extensions
            and not filepath.name.startswith(".")
            and "node_modules" not in str(filepath)
            and ".next" not in str(filepath)
        )

    def extract_imports(self, filepath: Path) -> List[str]:
        """Extract import statements from a JavaScript/TypeScript file."""
        imports = []

        try:
            with open(filepath, "r", encoding="utf-8") as file:
                content = file.read()

            # Remove comments to avoid false positives
            content = re.sub(r"//.*$", "", content, flags=re.MULTILINE)
            content = re.sub(r"/\*.*?\*/", "", content, flags=re.DOTALL)

            # Match various import patterns
            import_patterns = [
                # import ... from '...'
                r'import\s+(?:.*?\s+from\s+)?[\'"]([^\'"]+)[\'"]',
                # require('...')
                r'require\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\)',
                # dynamic import()
                r'import\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\)',
                # Next.js dynamic imports
                r'dynamic\s*\(\s*\(\s*\)\s*=>\s*import\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\)',
            ]

            for pattern in import_patterns:
                matches = re.findall(pattern, content, re.MULTILINE)
                imports.extend(matches)

        except Exception as e:
            print(f"Error reading {filepath}: {e}")

        return imports

    def resolve_import_path(
        self, import_path: str, current_file: Path
    ) -> Optional[Path]:
        """Resolve import path to actual file path."""
        current_dir = current_file.parent
        resolved_path = None

        # Handle relative imports (starting with . or ..)
        if import_path.startswith("./") or import_path.startswith("../"):
            resolved_path = (current_dir / import_path).resolve()

        # Handle absolute imports from root (starting with /)
        elif import_path.startswith("/"):
            resolved_path = (self.root_path / import_path.lstrip("/")).resolve()

        # Handle project-relative imports (no leading . or /)
        else:
            # First try from current directory
            test_from_current = (current_dir / import_path).resolve()
            if self._check_file_exists(test_from_current):
                resolved_path = test_from_current
            else:
                # Try from project root
                test_from_root = (self.root_path / import_path).resolve()
                if self._check_file_exists(test_from_root):
                    resolved_path = test_from_root
                else:
                    # Try from src directory if it exists
                    src_path = self.root_path / "src"
                    if src_path.exists():
                        test_from_src = (src_path / import_path).resolve()
                        if self._check_file_exists(test_from_src):
                            resolved_path = test_from_src

        # If we found a potential path, validate it exists with proper extension
        if resolved_path:
            return self._resolve_with_extensions(resolved_path)

        return None

    def _check_file_exists(self, path: Path) -> bool:
        """Check if a file exists with any valid extension."""
        return self._resolve_with_extensions(path) is not None

    def _resolve_with_extensions(self, resolved_path: Path) -> Optional[Path]:
        """Try to resolve a path with different file extensions."""
        # If path already has extension and exists
        if resolved_path.suffix and resolved_path.exists():
            return resolved_path

        # Try different file extensions if no extension provided
        if not resolved_path.suffix:
            for ext in [".js", ".jsx", ".ts", ".tsx", ".mjs"]:
                test_path = resolved_path.with_suffix(ext)
                if test_path.exists():
                    return test_path

            # Check for index files
            for ext in [".js", ".jsx", ".ts", ".tsx"]:
                index_path = resolved_path / f"index{ext}"
                if index_path.exists():
                    return index_path

        return None

    def analyze_file(self, filepath: Path, depth: int = 0) -> Dict:
        """Analyze a single file and its imports recursively."""
        relative_path = str(filepath.relative_to(self.root_path))

        # Avoid infinite recursion
        if relative_path in self.processed_files or depth > 20:
            return {"path": relative_path, "imports": {}, "circular": True}

        self.processed_files.add(relative_path)

        imports = self.extract_imports(filepath)
        import_tree = {}

        for import_path in imports:
            resolved_path = self.resolve_import_path(import_path, filepath)

            if resolved_path and self.is_valid_file(resolved_path):
                try:
                    relative_resolved = str(resolved_path.relative_to(self.root_path))
                    import_tree[import_path] = self.analyze_file(
                        resolved_path, depth + 1
                    )
                except ValueError:
                    # File is outside project root - skip it
                    continue
            # Skip external packages entirely - only include local unresolved files
            elif not self._is_external_package(import_path):
                import_tree[import_path] = {"unresolved": True, "path": import_path}

        # Only count local imports (resolved + unresolved non-external)
        local_imports = [k for k, v in import_tree.items()]

        return {
            "path": relative_path,
            "imports": import_tree,
            "import_count": len(local_imports),
        }

    def _is_external_package(self, import_path: str) -> bool:
        """Determine if an import is an external npm package."""
        # External packages typically don't start with . / or any local path indicators
        # and don't contain file path separators in the package name part
        if import_path.startswith(".") or import_path.startswith("/"):
            return False

        # Check if it looks like a scoped package (@scope/package) or regular package
        parts = import_path.split("/")
        first_part = parts[0]

        # Scoped packages start with @
        if first_part.startswith("@"):
            return True

        # Common external packages patterns
        external_indicators = [
            "react",
            "next",
            "lodash",
            "axios",
            "moment",
            "express",
            "fs",
            "path",
            "url",
            "crypto",
            "util",
            "os",
            "http",
            "https",
        ]

        # If it's a known external package
        if first_part in external_indicators:
            return True

        # If import contains no path separators, it's likely an npm package
        # But if it contains paths and we couldn't resolve it locally, it might be unresolved local
        if len(parts) == 1:
            return True

        return False

    def find_entry_points(self) -> List[Path]:
        """Find all page files in Next.js pages directory."""
        entry_points = []

        # Look for pages directories
        pages_dirs = []
        for pages_dir in ["pages", "src/pages"]:
            pages_path = self.root_path / pages_dir
            if pages_path.exists():
                pages_dirs.append(pages_path)

        # Also check for app directory (App Router)
        for app_dir in ["app", "src/app"]:
            app_path = self.root_path / app_dir
            if app_path.exists():
                pages_dirs.append(app_path)

        # Get all page files from these directories
        for pages_dir in pages_dirs:
            for file in pages_dir.rglob("*"):
                if self.is_valid_file(file):
                    # Skip API routes, middleware, and config files
                    relative_path = str(file.relative_to(pages_dir))
                    if not any(
                        skip in relative_path
                        for skip in [
                            "api/",
                            "_middleware",
                            ".config",
                            "_document",
                            "_error",
                        ]
                    ):
                        entry_points.append(file)

        # If no pages found, fall back to scanning common directories
        if not entry_points:
            for scan_dir in self.scan_dirs:
                scan_path = self.root_path / scan_dir
                if scan_path.exists():
                    for file in scan_path.rglob("*"):
                        if self.is_valid_file(file):
                            entry_points.append(file)

        return sorted(list(set(entry_points)))  # Remove duplicates and sort

    def generate_tree(self, entry_points: List[str] = None) -> Dict:
        """Generate the complete import tree."""
        if entry_points:
            files_to_analyze = [Path(self.root_path / ep) for ep in entry_points]
        else:
            files_to_analyze = self.find_entry_points()

        if not files_to_analyze:
            print("No entry points found. Scanning all JavaScript/TypeScript files...")
            files_to_analyze = []
            for scan_dir in self.scan_dirs:
                scan_path = self.root_path / scan_dir
                if scan_path.exists():
                    for file in scan_path.rglob("*"):
                        if self.is_valid_file(file):
                            files_to_analyze.append(file)

        tree = {}
        # Process each file separately to avoid cross-contamination
        for filepath in files_to_analyze:
            if filepath.exists():
                self.processed_files.clear()  # Reset for each entry point
                relative_path = str(filepath.relative_to(self.root_path))
                tree[relative_path] = self.analyze_file(filepath)

        return tree

    def print_tree(self, tree: Dict, indent: int = 0, visited: Set[str] = None):
        """Print the import tree in a readable format."""
        if visited is None:
            visited = set()

        for key, value in tree.items():
            prefix = "  " * indent + "├── " if indent > 0 else ""

            if isinstance(value, dict) and "path" in value:
                path = value["path"]
                circular = value.get("circular", False)
                unresolved = value.get("unresolved", False)
                import_count = value.get("import_count", 0)

                status = ""
                if circular:
                    status = " (circular)"
                elif unresolved:
                    status = " (unresolved)"
                elif import_count > 0:
                    status = f" ({import_count} imports)"

                print(f"{prefix}{key} -> {path}{status}")

                if (
                    not circular
                    and not unresolved
                    and path not in visited
                    and "imports" in value
                ):
                    visited.add(path)
                    self.print_tree(value["imports"], indent + 1, visited)
            else:
                print(f"{prefix}{key}")

    def save_to_json(self, tree: Dict, filename: str = "import_tree.json"):
        """Save the import tree to a JSON file."""
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(tree, f, indent=2, ensure_ascii=False)
        print(f"Import tree saved to {filename}")
