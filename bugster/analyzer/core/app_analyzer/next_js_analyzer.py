import fnmatch
import glob
import json
import os
import re
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from bugster.analyzer.cache import DOT_BUGSTER_DIR_PATH
from bugster.analyzer.utils.get_git_info import get_git_info


@dataclass
class LayoutInfo:
    name: str
    relative_file_path: str
    relative_dir_path: str
    content: str
    components: List[str]


@dataclass
class PageInfo:
    route_path: str
    relative_file_path: str
    components: List[str]
    has_params: bool
    has_form_submission: bool


@dataclass
class ApiInfo:
    route_path: str
    relative_file_path: str
    methods: List[str]
    input_validation: bool
    dependencies: List[str]


@dataclass
class FileInfo:
    relative_file_path: str
    relative_dir_path: str
    absolute_file_path: str
    name: str
    extension: str
    content: Optional[str] = None
    ast_parsed: Optional[Any] = None


@dataclass
class FrameworkInfo:
    id: str
    name: str
    version: str
    dir_path: str


@dataclass
class FileAnalysisResult:
    framework: str
    path: str
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AppAnalysis:
    framework: FrameworkInfo
    router_type: str
    stats: Dict[str, int]
    layouts: List[LayoutInfo]
    routes: List[Dict[str, Any]]
    api_routes: List[Dict[str, Any]]
    all_paths: List[str]


def assert_defined(value: Optional[Any]) -> Any:
    if value is None:
        raise ValueError("Expected a defined value, but got None")
    return value


def get_paths(dir_path: str) -> List[str]:
    """Get all file paths in a directory, excluding test files, specific directories,
    and respecting .gitignore rules.
    """
    # Process gitignore using pathspec
    try:
        import pathspec

        # Read .gitignore file if it exists
        gitignore_path = os.path.join(dir_path, ".gitignore")
        if os.path.exists(gitignore_path):
            with open(gitignore_path, "r") as f:
                gitignore = pathspec.PathSpec.from_lines(
                    pathspec.patterns.GitWildMatchPattern, f.readlines()
                )
        else:
            gitignore = None
    except ImportError:
        gitignore = None

    # Change to the directory for proper relative paths
    original_dir = os.getcwd()
    os.chdir(dir_path)

    # Get all files
    all_paths = glob.glob("**/*", recursive=True)

    # Ignore patterns matching the JavaScript version
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

    # Filter out ignored paths
    paths = []
    for path in all_paths:
        # Skip directories
        if os.path.isdir(path):
            continue

        # Skip ignored files based on patterns
        if any(fnmatch.fnmatch(path, pattern) for pattern in ignore_patterns):
            continue

        # Skip files ignored by gitignore
        if gitignore and gitignore.match_file(path):
            continue

        # Normalize path separators to forward slashes
        normalized_path = path.replace(os.sep, "/")
        paths.append(normalized_path)

    # Sort the paths
    paths.sort()

    # Change back to original directory
    os.chdir(original_dir)

    return paths


class TreeNode:
    def __init__(self, name: str, path: str, node_type: str):
        self.name = name
        self.path = path
        self.type = node_type
        self.children = []
        self.extension = os.path.splitext(name)[1] if node_type == "file" else None


def get_tree_structure(source_dir):
    """Get the tree structure of the source directory."""
    print("Building application structure tree...")
    paths = get_paths(dir_path=source_dir)
    root_node = {
        "path": "",
        "name": os.path.basename(source_dir),
        "type": "directory",
        "children": [],
    }
    dir_map = {"": root_node}

    def ensure_directory_path(dir_path):
        """Helper function to ensure a directory path exists in the tree and returns the node for that directory."""
        # If we already have this directory in our map, return it
        if dir_path in dir_map:
            return dir_map[dir_path]

        parent_path = os.path.dirname(dir_path)
        parent_node = (
            root_node if parent_path == "." else ensure_directory_path(parent_path)
        )
        dir_name = os.path.basename(dir_path)
        dir_node = {
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
            file_node = {
                "path": file_path,
                "name": file_name,
                "type": "file",
                "extension": os.path.splitext(file_path)[1],
            }
            parent_node["children"].append(file_node)

    return root_node


class NextJsAnalyzer:
    """Analyze the Next.js application."""

    def __init__(self, framework_info: FrameworkInfo):
        self.layouts: Dict[str, LayoutInfo] = {}
        self.routes: List[str] = []
        self.api_routes: List[str] = []
        self.results: List[FileAnalysisResult] = []
        self.pages: List[PageInfo] = []
        self.paths: List[str] = []
        self.apis: List[ApiInfo] = []
        self.is_app_router = False
        self.is_pages_router = False
        self.file_infos: List[FileInfo] = []
        self.NEXT_ANALYSIS_VERSION = 2
        self.framework_info = framework_info
        self.cache_framework_dir = os.path.join(
            DOT_BUGSTER_DIR_PATH, self.framework_info["id"]
        )

    def execute(self) -> AppAnalysis:
        """Execute the Next.js analyzer."""
        print("Executing NextJs analyzer")
        self.layouts = {}
        self.routes = []
        self.api_routes = []
        self.pages = []
        self.paths = []
        self.apis = []
        self.is_app_router = False
        self.is_pages_router = False
        self.set_paths()
        self.set_tree_structure()
        print(f"Processing {len(self.file_infos)} files")
        self.detect_router_type()
        self.parse_files()
        self.process_layout_files()
        self.process_route_files()
        print(
            f"Analysis generated: {len(self.pages)} pages, "
            f"{len(self.apis)} API routes, {len(self.layouts)} layouts"
        )
        analysis = self.generate_analysis()
        self.save_analysis_to_file(analysis)
        return analysis

    def set_paths(self) -> None:
        """Set the paths for the NextJs analyzer."""
        print("Retrieving folder paths for NextJs analyzer...")
        self.paths = get_paths(dir_path=self.framework_info["dir_path"])
        os.makedirs(self.cache_framework_dir, exist_ok=True)
        paths_output = {
            "metadata": {
                "timestamp": time.time(),
                "version": self.NEXT_ANALYSIS_VERSION,
                "git": get_git_info(),
            },
            "data": {
                "framework": self.framework_info,
                "paths": self.paths,
            },
        }

        with open(os.path.join(self.cache_framework_dir, "paths.json"), "w") as f:
            json.dump(paths_output, f, indent=2)

        print(
            "Paths saved",
            {
                "path": os.path.join(self.cache_framework_dir, "paths.json"),
            },
        )

    def set_tree_structure(self) -> None:
        """Set the tree structure for the NextJs analyzer."""
        print("Building tree structure for NextJs analyzer...")

        try:
            tree_node = get_tree_structure(self.framework_info["dir_path"])
            self.set_file_infos(tree_node)
            os.makedirs(self.cache_framework_dir, exist_ok=True)
            tree_json_path = os.path.join(self.cache_framework_dir, "tree.json")

            # Convert TreeNode to dict for JSON serialization
            def node_to_dict(node):
                result = {
                    "name": node["name"],
                    "path": node["path"],
                    "type": node["type"],
                }

                if "extension" in node:
                    result["extension"] = node["extension"]

                if "children" in node:
                    result["children"] = [
                        node_to_dict(child) for child in node["children"]
                    ]

                return result

            tree_output = {
                "metadata": {
                    "timestamp": time.time(),
                    "version": self.NEXT_ANALYSIS_VERSION,
                    "git": get_git_info(),
                },
                "data": {
                    "framework": self.framework_info,
                    "node": node_to_dict(tree_node),
                },
            }

            with open(tree_json_path, "w") as f:
                json.dump(tree_output, f, indent=2)

            print("Tree structure saved", {"path": tree_json_path})
        except Exception as error:
            print("Failed to build tree structure", error)
            raise error

    def set_file_infos(self, node: TreeNode) -> None:
        """Set the file infos for the NextJs analyzer."""
        if node.get("type") == "directory" and node["children"]:
            for child in node["children"]:
                self.set_file_infos(child)
        elif node.get("type") == "file":
            self.file_infos.append(
                FileInfo(
                    relative_file_path=node.get("path"),
                    relative_dir_path=os.path.dirname(node.get("path")),
                    absolute_file_path=os.path.join(
                        self.framework_info["dir_path"], node["path"]
                    ),
                    name=node.get("name"),
                    extension=node.get("extension"),
                    content=None,
                    ast_parsed=None,
                )
            )

    def generate_analysis(self) -> AppAnalysis:
        """Generate the analysis for the NextJs analyzer."""
        route_info_list = [
            {
                "routePath": page.route_path,
                "relativeFilePath": page.relative_file_path,
                "layoutChain": self.get_layout_chain_for_page(page.relative_file_path),
                "components": page.components,
                "hasParams": page.has_params,
                "hasForm": page.has_form_submission,
                "hooks": self.get_hooks_for_file(page.relative_file_path),
                "eventHandlers": self.get_event_handlers_for_file(
                    page.relative_file_path
                ),
                "featureFlags": [],
            }
            for page in self.pages
        ]
        api_route_info_list = [
            {
                "routePath": api.route_path,
                "relativeFilePath": api.relative_file_path,
                "methods": api.methods,
                "hasValidation": api.input_validation,
                "deps": api.dependencies,
            }
            for api in self.apis
        ]
        layout_info_list = list(self.layouts.values())
        return AppAnalysis(
            framework=self.framework_info,
            router_type=(
                "app"
                if self.is_app_router
                else "pages"
                if self.is_pages_router
                else "unknown"
            ),
            stats={
                "fileCount": len(self.file_infos),
                "routeCount": len(self.pages),
                "apiRouteCount": len(self.apis),
                "layoutCount": len(self.layouts),
            },
            layouts=layout_info_list,
            routes=route_info_list,
            api_routes=api_route_info_list,
            all_paths=self.paths,
        )

    def get_layout_chain_for_page(self, filepath: str) -> List[str]:
        """Get the layout chain for a page."""
        file_dir_path = os.path.dirname(filepath)
        layout_info = [
            {
                "name": name,
                "relative_dir_path": layout.relative_dir_path,
                "distance": self.get_directory_distance(
                    file_dir_path, layout.relative_dir_path
                ),
            }
            for name, layout in self.layouts.items()
        ]
        filtered_layouts = [layout for layout in layout_info if layout["distance"] >= 0]
        sorted_layouts = sorted(filtered_layouts, key=lambda x: x["distance"])
        return [layout["name"] for layout in sorted_layouts]

    def get_directory_distance(self, from_path: str, to_path: str) -> int:
        """Get the distance between two directories."""
        # If 'to' is not a parent directory of 'from', return -1
        if not from_path.startswith(to_path):
            return -1

        # Count directory levels between 'from' and 'to'
        from_parts = from_path.split("/")
        to_parts = to_path.split("/")
        return len(from_parts) - len(to_parts)

    def get_hooks_for_file(self, filepath: str) -> List[str]:
        """Get the hooks for a file."""
        result = next((r for r in self.results if r.path == filepath), None)
        return result.details.get("hooks", []) if result else []

    def get_event_handlers_for_file(self, filepath: str) -> List[str]:
        """Get the event handlers for a file."""
        result = next((r for r in self.results if r.path == filepath), None)
        return result.details.get("eventHandlers", []) if result else []

    def save_analysis_to_file(self, analysis: AppAnalysis) -> None:
        """Save the analysis to a file."""
        try:
            os.makedirs(self.cache_framework_dir, exist_ok=True)
            analysis_json_path = os.path.join(self.cache_framework_dir, "analysis.json")

            # Convert AppAnalysis to dict for JSON serialization
            def serialize_analysis(obj):
                if hasattr(obj, "__dict__"):
                    return {k: serialize_analysis(v) for k, v in obj.__dict__.items()}
                elif isinstance(obj, list):
                    return [serialize_analysis(item) for item in obj]
                elif isinstance(obj, dict):
                    return {k: serialize_analysis(v) for k, v in obj.items()}
                else:
                    return obj

            output = {
                "metadata": {
                    "timestamp": time.time(),
                    "version": self.NEXT_ANALYSIS_VERSION,
                    "git": get_git_info(),
                },
                "data": serialize_analysis(analysis),
            }

            with open(analysis_json_path, "w") as f:
                json.dump(output, f, indent=2)

            print(f"Analysis saved to {analysis_json_path}")
        except Exception as error:
            print("Failed to save analysis to file", error)
            raise error

    def parse_files(self) -> None:
        """Parse the files for the NextJs analyzer."""
        file_extensions = [".js", ".jsx", ".ts", ".tsx"]
        print(
            "Parsing eligible files",
            {
                "extensions": file_extensions,
            },
        )

        for ext in file_extensions:
            files = [file for file in self.file_infos if file.extension == ext]
            print(f"Found {len(files)} files with extension: {ext}")

            for file in files:
                try:
                    if not file.content:
                        try:
                            print("Reading file", {"path": file.relative_file_path})
                            with open(
                                os.path.join(
                                    self.framework_info["dir_path"],
                                    file.relative_file_path,
                                ),
                                "r",
                                encoding="utf-8",
                            ) as f:
                                file.content = f.read()
                        except Exception as read_error:
                            print(
                                f"Error reading file {file.relative_file_path}:",
                                read_error,
                            )
                            continue

                    if not file.ast_parsed and file.content:
                        try:
                            # Note: Python's ast module is not equivalent to
                            # JavaScript's babel parser, this is a simplification
                            # In a real implementation, you'd need a proper JS parser in Python
                            file.ast_parsed = file.content
                            # Placeholder for actual parsing - in reality we'd use
                            # a JS parser library like esprima-python
                        except Exception as parse_error:
                            print(
                                f"Error parsing file {file.relative_file_path}:",
                                parse_error,
                            )
                except Exception as error:
                    print(
                        f"Unexpected error processing file {file.relative_file_path}:",
                        error,
                    )

        print("File parsing complete")

    def process_layout_files(self) -> None:
        """Process the layout files for the NextJs analyzer."""
        layout_file_infos = [
            file
            for file in self.file_infos
            if re.match(r"^layout\.(jsx?|tsx)$", file.name)
        ]

        for layout_file_info in layout_file_infos:
            content = assert_defined(layout_file_info.content)

            # In a real implementation we'd use a JS parser
            # This is a simplified approach
            layout_name = self._extract_layout_name(
                content, layout_file_info.relative_file_path
            )

            if not layout_name:
                print(
                    "Could not determine layout name",
                    {
                        "path": layout_file_info.relative_file_path,
                    },
                )
                raise Exception(
                    f"Could not determine layout name: {layout_file_info.relative_file_path}"
                )

            layout_info = LayoutInfo(
                name=layout_name,
                relative_file_path=layout_file_info.relative_file_path,
                relative_dir_path=layout_file_info.relative_dir_path,
                content=content,
                components=self._extract_components_from_content(content),
            )
            self.layouts[layout_name] = layout_info

    def _extract_layout_name(self, content: str, file_path: str) -> Optional[str]:
        """Extract the layout name from the content."""
        # Simplified layout name extraction that looks for export default
        export_default_match = re.search(r"export\s+default\s+(\w+)", content)

        if export_default_match:
            return export_default_match.group(1)

        # Try to find function declaration with "Layout" in name
        layout_func_match = re.search(r"function\s+(\w*Layout\w*)\s*\(", content)

        if layout_func_match:
            return layout_func_match.group(1)

        # Fallback: use directory name + "Layout"
        parts = file_path.split("/")
        if len(parts) >= 2:
            dir_name = parts[-2]
            return dir_name[0].upper() + dir_name[1:] + "Layout"

        return "Layout"  # Last resort

    def _extract_components_from_content(self, content: str) -> List[str]:
        """Extract the components from the content."""
        # Simplified component extraction that looks for JSX components (capitalized tags)
        components = set()
        component_matches = re.findall(r"<([A-Z]\w+)", content)
        components.update(component_matches)
        return list(components)

    def detect_router_type(self) -> None:
        """Detect the router type for the NextJs analyzer."""
        self.is_app_router = any(
            file.relative_dir_path == "app" for file in self.file_infos
        )
        self.is_pages_router = any(
            file.relative_dir_path == "pages" for file in self.file_infos
        )

        if self.is_app_router and self.is_pages_router:
            print(
                "Detected both App Router and Pages Router. Prioritizing App Router for analysis."
            )
        elif self.is_app_router:
            print("Detected Next.js App Router")
        elif self.is_pages_router:
            print("Detected Next.js Pages Router")
        else:
            print("Could not determine Next.js router type")

    def process_route_files(self) -> None:
        """Process the route files for the NextJs analyzer."""
        print(
            "Processing route files",
            {
                "is_app_router": self.is_app_router,
                "is_pages_router": self.is_pages_router,
            },
        )
        ROUTING_FILE_PATTERNS = [
            r"layout\.(js|jsx|tsx)$",
            r"page\.(js|jsx|tsx)$",
            r"loading\.(js|jsx|tsx)$",
            r"not-found\.(js|jsx|tsx)$",
            r"error\.(js|jsx|tsx)$",
            r"global-error\.(js|jsx|tsx)$",
            r"route\.(js|ts)$",
            r"template\.(js|jsx|tsx)$",
            r"default\.(js|jsx|tsx)$",
        ]
        app_router_files = [
            file
            for file in self.file_infos
            if any(re.search(pattern, file.name) for pattern in ROUTING_FILE_PATTERNS)
        ]

        if app_router_files or self.is_app_router:
            self.is_app_router = True
            print(f"Found {len(app_router_files)} App Router files")

            for file in app_router_files:
                self.process_app_router_file(file)

        pages_files = [
            file
            for file in self.file_infos
            if (
                "/pages/" in file.relative_dir_path
                or file.relative_dir_path.startswith("pages/")
            )
            and not file.name.startswith("_")
            and file.name != "api"
        ]

        if pages_files or self.is_pages_router:
            self.is_pages_router = True
            print(f"Found {len(pages_files)} Pages Router files")

            for file in pages_files:
                self.process_pages_router_file(file)

        api_files = [
            file for file in self.file_infos if "/api/" in file.relative_file_path
        ]
        print(f"Found {len(api_files)} API files")

        for file in api_files:
            if file.relative_file_path.startswith("pages/api/"):
                self.process_pages_router_file(file)
            else:
                self.process_app_router_file(file)

        print(
            f"Processed {len(self.routes)} routes and {len(self.api_routes)} API routes"
        )

    def process_app_router_file(self, file: FileInfo) -> None:
        """Process the app router file for the NextJs analyzer."""
        if not file.content:
            return

        file_detail = FileAnalysisResult(
            framework="next",
            path=file.relative_file_path,
            details={
                "isRoute": False,
                "isApiRoute": False,
                "isLayout": False,
                "components": [],
                "imports": [],
                "exports": [],
                "hooks": [],
                "eventHandlers": [],
            },
        )

        # Simplified extraction methods that would use regex patterns
        # in a real implementation
        file_detail.details["imports"] = self._extract_imports_from_content(
            file.content
        )
        file_detail.details["exports"] = self._extract_exports_from_content(
            file.content
        )
        file_detail.details["hooks"] = self._extract_hooks_from_content(file.content)
        file_detail.details["eventHandlers"] = (
            self._extract_event_handlers_from_content(file.content)
        )
        file_detail.details["components"] = self._extract_components_from_content(
            file.content
        )

        if file.name in ["page.js", "page.tsx"]:
            file_detail.details["isRoute"] = True
            route_path = self.get_route_path_from_file_app(file.relative_file_path)
            self.routes.append(route_path)

            page_info = PageInfo(
                route_path=route_path,
                relative_file_path=file.relative_file_path,
                components=file_detail.details["components"] or [],
                has_params=self.has_route_params(route_path),
                has_form_submission=self.has_form_submission_in_content(file.content),
            )

            self.pages.append(page_info)
            file_detail.details["pageInfo"] = page_info.__dict__
        elif file.name in ["layout.js", "layout.tsx"]:
            file_detail.details["isLayout"] = True

            layout_name = None
            exports = self._extract_exports_from_content(file.content)
            default_export = next((e for e in exports if "(default)" in e), None)

            if default_export:
                layout_name = default_export.replace(" (default)", "")

            if not layout_name:
                parts = file.relative_file_path.split("/")
                dir_name = parts[-2] if len(parts) >= 2 else ""
                layout_name = (
                    dir_name[0].upper() + dir_name[1:] + "Layout"
                    if dir_name
                    else "Layout"
                )

            if file.relative_file_path in ["app/layout.tsx", "app/layout.js"]:
                layout_name = "RootLayout"
        elif (
            file.name in ["route.js", "route.tsx"] or "/api/" in file.relative_file_path
        ):
            file_detail.details["isApiRoute"] = True
            route_path = self.get_route_path_from_file_app(file.relative_file_path)
            self.api_routes.append(route_path)

            api_info = ApiInfo(
                route_path=route_path,
                relative_file_path=file.relative_file_path,
                methods=self._extract_api_methods_from_content(file.content),
                input_validation=self.has_input_validation_in_content(file.content),
                dependencies=file_detail.details["imports"] or [],
            )

            self.apis.append(api_info)
            file_detail.details["apiInfo"] = api_info.__dict__

        self.results.append(file_detail)

    def process_pages_router_file(self, file: FileInfo) -> None:
        """Process the pages router file for the NextJs analyzer."""
        if not file.content:
            return

        file_detail = FileAnalysisResult(
            framework="next",
            path=file.relative_file_path,
            details={
                "isRoute": False,
                "isApiRoute": False,
                "components": [],
                "imports": [],
                "exports": [],
                "hooks": [],
                "eventHandlers": [],
            },
        )

        file_detail.details["imports"] = self._extract_imports_from_content(
            file.content
        )
        file_detail.details["exports"] = self._extract_exports_from_content(
            file.content
        )
        file_detail.details["hooks"] = self._extract_hooks_from_content(file.content)
        file_detail.details["eventHandlers"] = (
            self._extract_event_handlers_from_content(file.content)
        )
        file_detail.details["components"] = self._extract_components_from_content(
            file.content
        )

        # Check for _app.js/_app.tsx which could be considered a layout
        if file.name in ["_app.js", "_app.tsx"]:
            self.layouts["PagesAppLayout"] = LayoutInfo(
                name="PagesAppLayout",
                relative_file_path=file.relative_file_path,
                relative_dir_path=file.relative_dir_path,
                content=file.content or "",
                components=self._extract_components_from_content(file.content or ""),
            )

        if file.relative_file_path.startswith("pages/api/"):
            file_detail.details["isApiRoute"] = True
            route_path = self.get_route_path_from_file_pages(file.relative_file_path)
            self.api_routes.append(route_path)
            api_info = ApiInfo(
                route_path=route_path,
                relative_file_path=file.relative_file_path,
                methods=self._extract_api_methods_from_content(file.content),
                input_validation=self.has_input_validation_in_content(file.content),
                dependencies=file_detail.details["imports"] or [],
            )
            self.apis.append(api_info)
            file_detail.details["apiInfo"] = api_info.__dict__
        else:
            file_detail.details["isRoute"] = True
            route_path = self.get_route_path_from_file_pages(file.relative_file_path)
            self.routes.append(route_path)
            page_info = PageInfo(
                route_path=route_path,
                relative_file_path=file.relative_file_path,
                components=file_detail.details["components"] or [],
                has_params=self.has_route_params(route_path),
                has_form_submission=self.has_form_submission_in_content(file.content),
            )
            self.pages.append(page_info)
            file_detail.details["pageInfo"] = page_info.__dict__

        self.results.append(file_detail)

    def _extract_imports_from_content(self, content: str) -> List[str]:
        """Extract the imports from the content."""
        # Simplified import extraction using regex
        imports = []

        for match in re.finditer(r"import\s+(?:{([^}]+)}|([^{}\s;]+))\s+from", content):
            if match.group(1):  # Named imports
                for name in re.findall(r"(\w+)", match.group(1)):
                    imports.append(name)
            elif match.group(2):  # Default import
                imports.append(match.group(2))

        return imports

    def _extract_exports_from_content(self, content: str) -> List[str]:
        """Extract the exports from the content."""
        # Simplified export extraction using regex
        exports = []

        # Named exports
        for match in re.finditer(r"export\s+(const|let|var|function)\s+(\w+)", content):
            exports.append(match.group(2))

        # Default exports
        for match in re.finditer(r"export\s+default\s+(?:function\s+)?(\w+)", content):
            exports.append(f"{match.group(1)} (default)")

        # Default exports of variables/consts
        for match in re.finditer(r"export\s+default\s+(\w+)", content):
            if match.group(1) not in [
                exp.split()[0] for exp in exports if "(default)" in exp
            ]:
                exports.append(f"{match.group(1)} (default)")

        if not any("default" in exp for exp in exports) and "export default" in content:
            exports.append("(anonymous default export)")

        return exports

    def _extract_hooks_from_content(self, content: str) -> List[str]:
        # Find React hooks (functions starting with "use" followed by uppercase)
        hooks = []
        for match in re.finditer(r"\b(use[A-Z]\w*)\s*\(", content):
            hook = match.group(1)
            if hook not in hooks:
                hooks.append(hook)
        return hooks

    def _extract_event_handlers_from_content(self, content: str) -> List[str]:
        """Extract the event handlers from the content.

        TODO: This is a workaround that MUST be improved.
        """
        # Find event handlers based on naming patterns
        handlers = []

        # Function declarations
        for match in re.finditer(
            r"(?:function|const|let|var)\s+((handle|on)[A-Z]\w*|\w+(Click|Change|Submit|Focus|Blur))",
            content,
        ):
            handler = match.group(1)
            if handler not in handlers:
                handlers.append(handler)

        return handlers

    def has_form_submission_in_content(self, content: str) -> bool:
        """Check if the content has a form submission."""
        # Check for form elements or onSubmit handlers
        return bool(
            re.search(r"<form", content)
            or re.search(r"onSubmit", content)
            or re.search(r"handleSubmit", content)
        )

    def _extract_api_methods_from_content(self, content: str) -> List[str]:
        """Extract the API methods from the content."""
        # Extract HTTP methods from API route handlers
        methods = []

        # Look for req.method references
        for method in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
            if re.search(
                rf"req\.method\s*===?\s*['\"]({method})['\"]", content, re.IGNORECASE
            ):
                methods.append(method)

        # Look for specific method handlers or express-like route handlers
        for method in ["get", "post", "put", "delete", "patch"]:
            if re.search(rf"\b{method}\s*\(", content, re.IGNORECASE):
                methods.append(method.upper())

        return list(set(methods))

    def has_input_validation_in_content(self, content: str) -> bool:
        """Check if the content has input validation."""
        # Check for common validation libraries or patterns
        validation_patterns = [
            r"\bvalidate\b",
            r"\bschema\b",
            r"\byup\b",
            r"\bzod\b",
            r"\bjoi\b",
        ]

        return any(re.search(pattern, content) for pattern in validation_patterns)

    def has_route_params(self, route: str) -> bool:
        """Check if the route has route params."""
        return ":" in route

    def get_route_path_from_file_app(self, file_path: str) -> str:
        """Get the route path from the file path."""
        # Transform app/dashboard/settings/page.tsx -> /dashboard/settings
        route_path = re.sub(r"^app", "", file_path)
        route_path = re.sub(r"/(page|route|layout)\.(js|jsx|ts|tsx)$", "", route_path)

        # Handle dynamic route params
        route_path = re.sub(r"/\[([^\]]+)\]", r"/:\1", route_path)

        return route_path or "/"

    def get_route_path_from_file_pages(self, file_path: str) -> str:
        """Get the route path from the file path."""
        # Transform pages/dashboard/settings.tsx -> /dashboard/settings
        route_path = re.sub(r"^pages", "", file_path)
        route_path = re.sub(r"\.(js|jsx|ts|tsx)$", "", route_path)

        # Handle dynamic route params
        route_path = re.sub(r"/\[([^\]]+)\]", r"/:\1", route_path)

        # Handle index routes
        route_path = re.sub(r"/index$", "", route_path)

        return route_path or "/"
